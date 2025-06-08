import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urljoin, urlparse
import os
import re

def sanitize_filename(filename):
    """Remove or change invalid characters for a filename."""
    filename = str(filename)
    filename = re.sub(r'\s+', '_', filename)
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'_+', '_', filename)
    filename = filename.strip('_')
    if not filename: # If it's completely empty, give it a default name
        filename = "untitled"
    return filename

def get_file_extension_from_url_or_content_type(url, response_headers):
    """Guess the file extension from the URL or Content-Type."""
    path = urlparse(url).path
    _, ext = os.path.splitext(path) # Only get the extension
    if ext and len(ext) > 1 and ext[1:].isalnum(): # Check if it's a valid extension
        return ext.lower()

    content_type = response_headers.get('content-type')
    if content_type:
        if 'image/jpeg' in content_type: return '.jpg'
        if 'image/png' in content_type: return '.png'
        if 'image/gif' in content_type: return '.gif'
        if 'image/webp' in content_type: return '.webp'
        if 'image/svg+xml' in content_type: return '.svg'
    return '.jpg'

def extract_and_save_subpage_links(soup, page_url, output_txt_filepath):
    """
    Extract and save subpage links from the given BeautifulSoup object and the main URL.
    """
    print(f"  Extracting subpage links...{output_txt_filepath}")
    found_links = set()

    # For finding the navigation menu, we use a more specific targeting
    # The HTML you provided contains a div with the class "md:sticky" and "md:block"
    # and contains ul elements with the class "space-y-1"
    nav_panel = soup.find('div', class_=lambda c: c and 'md:sticky' in c and 'md:block' in c)

    if not nav_panel:
        # Alternative: Maybe we can directly search for ul tags
        # This might be more site-specific
        nav_ul_candidates = soup.find_all('ul', class_=lambda c: c and 'space-y-1' in c)
        # Usually the navigation is on the left, so we can select the first suitable ul
        # Alternatively, we can search for 'nav' tags with more complex logic
        # For now, if we can't find the md:sticky div, try the first space-y-1 ul
        if nav_ul_candidates:
            nav_panel = nav_ul_candidates[0] # Select the first suitable ul
        else:
            print(f"    Warning: Navigation panel (md:sticky div or space-y-1 ul) not found.")
            # If we can't find anything, we can try to extract all links from the page
            # but this might get us a lot of irrelevant links. For now, this is enough.
            # For a more robust solution, one might need to inspect various page structures.
            return False


    # Determine the base path (e.g. /lokumai/openai-openapi-template)
    # This is used to only extract links within the same project/wiki
    parsed_page_url = urlparse(page_url)
    path_segments = [seg for seg in parsed_page_url.path.split('/') if seg]
    project_base_path = ""
    if len(path_segments) >= 2: # Usually in the form of /username/project
        project_base_path = f"/{path_segments[0]}/{path_segments[1]}"
    
    # Sometimes the base path might be shorter or have a different structure.
    # This might need to be adjusted based on the site's general URL structure.
    # For example, if all links are under /wiki/, project_base_path = "/wiki" might be used.
    # For DeepWiki, the /username/project_name/ pattern usually works.

    for link_tag in nav_panel.find_all('a', href=True):
        href = link_tag['href']
        # Extract valid, non-internal, and within the same domain/project links
        if href and not href.startswith('#') and \
           not href.startswith('mailto:') and \
           not href.startswith('javascript:'):
            
            full_url = urljoin(page_url, href)
            parsed_full_url = urlparse(full_url)

            # Extract only links within the same domain and (if determined) within the same project base path
            is_same_domain = parsed_full_url.netloc == parsed_page_url.netloc
            is_within_project = True # Default to true
            if project_base_path: # If we were able to determine a project base path
                 is_within_project = parsed_full_url.path.startswith(project_base_path)
            
            # Sometimes links are provided as full URLs (another wiki page but same domain)
            # In this case, project_base_path check is important.
            # If project_base_path cannot be determined (e.g. homepage), only domain check might be enough.

            if is_same_domain and is_within_project:
                # We might not want to include links to itself (optional)
                # if full_url.rstrip('/') != page_url.rstrip('/'):
                found_links.add(full_url)

    if found_links:
        # Delete old link file (if it exists and will be overwritten)
        if os.path.exists(output_txt_filepath):
            try:
                os.remove(output_txt_filepath)
            except OSError as e:
                print(f"    Warning: Old link file ({output_txt_filepath}) could not be deleted: {e}")

        with open(output_txt_filepath, 'w', encoding='utf-8') as f:
            for link in sorted(list(found_links)):
                f.write(link + "\n")
        print(f"    {len(found_links)} subpage links saved to '{output_txt_filepath}' file.")
        return True
    else:
        print(f"    No valid subpage links found.")
        return False


def process_deepwiki_page(page_url, output_dir="output"):
    """
    Extract the content from the given DeepWiki URL, convert it to Markdown,
    download images, extract subpage links, and save them to the specified output directory.
    """
    print(f"\nProcessing: {page_url}")
    try:
        response = requests.get(page_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print(f"Error: Timeout - {page_url}")
        return False, None # Failed, soup object is None
    except requests.exceptions.RequestException as e:
        print(f"Error: Page could not be downloaded - {page_url}. {e}")
        return False, None # Failed, soup object is None

    soup = BeautifulSoup(response.content, 'html.parser')

    content_div = soup.find('div', class_='prose max-w-none dark:prose-invert')
    if not content_div:
        main_title_h1 = soup.find('h1')
        if main_title_h1:
            print(f"Warning: Main content area ('prose' div) not found - {page_url}. Trying content around the title.")
            # This might be site-specific. For now, a more general fallback:
            content_div = main_title_h1.find_parent('article') or \
                          main_title_h1.find_parent('main') or \
                          main_title_h1.parent # Worst case, the direct parent of the title
            if not content_div: content_div = soup.body # Last resort
        else:
            print(f"Error: Main content area ('prose' div) and H1 title not found - {page_url}.")
            return False, soup # Error but return the soup object so links can be extracted
    
    page_title_tag = content_div.find(['h1', 'h2']) if content_div else soup.find(['h1', 'h2'])
    if page_title_tag and page_title_tag.get_text(strip=True):
        base_filename = sanitize_filename(page_title_tag.get_text(strip=True))
    else:
        path_segments = [seg for seg in urlparse(page_url).path.split('/') if seg]
        base_filename_suggestion = path_segments[-1] if path_segments else "page"
        base_filename = sanitize_filename(base_filename_suggestion)
    
    if not base_filename: base_filename = "untitled_page"

    # For each page, create a separate folder (under output_dir)
    # e.g. output_dir/1-overview/
    page_specific_output_dir = os.path.join(output_dir, base_filename)
    
    # Subfolder for images (under page_specific_output_dir)
    # e.g. output_dir/1-overview/1-overview-images/
    images_subfolder_name = f"{base_filename}-images"
    images_full_dir = os.path.join(page_specific_output_dir, images_subfolder_name)

    if not os.path.exists(images_full_dir):
        os.makedirs(images_full_dir)
    
    md_filename = f"{base_filename}.md"
    md_filepath = os.path.join(page_specific_output_dir, md_filename)
    subpage_links_txt_filename = f"{base_filename}-subpages.txt"
    subpage_links_txt_filepath = os.path.join(page_specific_output_dir, subpage_links_txt_filename)

    print(f"  Markdown file: {md_filepath}")
    print(f"  Images folder: {images_full_dir}")
    print(f"  Subpage links file: {subpage_links_txt_filepath}")

    # Extract and save subpage links (before processing the Markdown content)
    extract_and_save_subpage_links(soup, page_url, subpage_links_txt_filepath)


    # Now process the Markdown content and images
    if content_div: # Only process if content_div exists
        for i, img_tag in enumerate(content_div.find_all('img')):
            src = img_tag.get('src')
            if not src or src.startswith('data:'): continue

            img_url = urljoin(page_url, src)
            try:
                img_response = requests.get(img_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
                img_response.raise_for_status()

                original_img_filename = os.path.basename(urlparse(img_url).path)
                if not original_img_filename or '.' not in original_img_filename: # If the URL has no filename or extension
                    base_name_from_url = sanitize_filename(original_img_filename.split('.')[0] if '.' in original_img_filename else original_img_filename or f"image_{i+1}")
                else:
                    base_name_from_url = sanitize_filename(os.path.splitext(original_img_filename)[0])

                img_ext = get_file_extension_from_url_or_content_type(img_url, img_response.headers)
                clean_img_filename = f"{base_name_from_url}{img_ext}"
                local_img_path_abs = os.path.join(images_full_dir, clean_img_filename)
                
                with open(local_img_path_abs, 'wb') as f:
                    for chunk in img_response.iter_content(chunk_size=8192): f.write(chunk)
                
                # Relative path for Markdown: [images_subfolder_name]/[clean_img_filename]
                relative_img_path_for_md = os.path.join(images_subfolder_name, clean_img_filename).replace("\\", "/")
                img_tag['src'] = relative_img_path_for_md

            except requests.exceptions.Timeout: print(f"    Error: Image could not be downloaded (timeout) - {img_url}")
            except requests.exceptions.RequestException as e: print(f"    Error: Image could not be downloaded - {img_url}. {e}")
            except IOError as e: print(f"    Error: Image file could not be written. {e}")
        
        markdown_content = md(str(content_div), heading_style='atx', bullets='*', strip=['script', 'style'])
        try:
            with open(md_filepath, 'w', encoding='utf-8') as f: f.write(markdown_content)
            print(f"  Successfully saved: {md_filepath}")
            return True, soup # Success, return the soup object
        except IOError as e:
            print(f"Error: Markdown file could not be written - {md_filepath}. {e}")
            return False, soup # Markdown saved but soup object is still returned
    else:
        print(f"  Warning: No content found, so Markdown and images could not be processed.")
        return False, soup # Markdown could not be processed


if __name__ == "__main__":
    url_list = [
        "https://deepwiki.com/lokumai/openai-openapi-template/1-overview",
        #"https://deepwiki.com/lokumai/openai-openapi-template/2-setup-and-installation",
        # "https://deepwiki.com/another/project/page"
    ]
    main_output_directory = "deepwiki_export_v2" # New folder name
    if not os.path.exists(main_output_directory):
        os.makedirs(main_output_directory)

    processed_urls = set() # To avoid reprocessing
    urls_to_crawl = list(url_list) # Start URLs, can grow over time
    
    max_pages_to_crawl = 10 # A limit to prevent infinite loop (optional)
    crawled_count = 0

    all_extracted_subpages = set() # All extracted subpage links

    queue_idx = 0
    while queue_idx < len(urls_to_crawl) and crawled_count < max_pages_to_crawl:
        current_url = urls_to_crawl[queue_idx]
        queue_idx += 1

        if current_url in processed_urls:
            print(f"Skipping (already processed): {current_url}")
            continue
        
        success, soup_obj = process_deepwiki_page(current_url, output_dir=main_output_directory)
        processed_urls.add(current_url)
        crawled_count += 1

        if soup_obj: # If the page was successfully downloaded (even if the content could not be processed)
            # `process_deepwiki_page` already extracts and saves links.
            # If you want to crawl these links in the next iteration:
            
            # We need to create the filename again
            page_title_tag = soup_obj.find(['h1', 'h2'])
            if page_title_tag and page_title_tag.get_text(strip=True):
                base_filename = sanitize_filename(page_title_tag.get_text(strip=True))
            else:
                path_segments = [seg for seg in urlparse(current_url).path.split('/') if seg]
                base_filename_suggestion = path_segments[-1] if path_segments else "page"
                base_filename = sanitize_filename(base_filename_suggestion)
            if not base_filename: base_filename = "untitled_page"

            page_specific_output_dir = os.path.join(main_output_directory, base_filename)
            subpage_links_txt_filename = f"{base_filename}-subpages.txt"
            subpage_links_txt_filepath = os.path.join(page_specific_output_dir, subpage_links_txt_filename)

            if os.path.exists(subpage_links_txt_filepath):
                with open(subpage_links_txt_filepath, 'r', encoding='utf-8') as f:
                    newly_found_links = {line.strip() for line in f if line.strip()}
                    all_extracted_subpages.update(newly_found_links)
                    for link in newly_found_links:
                        if link not in processed_urls and link not in urls_to_crawl[queue_idx:]: # Kuyrukta zaten yoksa ekle
                             urls_to_crawl.append(link)
        
        print("-" * 30)

    print("\n--- Process Completed ---")
    print(f"Total {crawled_count} pages processed.")
    print(f"All extracted subpage links (total {len(all_extracted_subpages)} links) saved to the relevant `*-subpages.txt` files.")
    # If you want to print all links to a single file:
    # consolidated_links_file = os.path.join(main_output_directory, "ALL_SUBPAGES.txt")
    # with open(consolidated_links_file, 'w', encoding='utf-8') as f:
    #     for link in sorted(list(all_extracted_subpages)):
    #         f.write(link + "\n")
    # print(f"All extracted subpage links also saved to '{consolidated_links_file}' file.")
    print(f"Output saved to '{main_output_directory}' folder.")