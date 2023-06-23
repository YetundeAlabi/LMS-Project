import re
from django import template

register = template.Library()

@register.filter
def extract_links(value):
    pattern = r'<a\s+(?:[^>]*?\s+)?href=(["\'])(.*?)\1'
    links = re.findall(pattern, value)
    return [link[1] for link in links]



@register.filter
def embed_video(content):
    video_regex = re.compile(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)')
    match = video_regex.search(content)
    if match:
        video_id = match.group(1)
        embed_code = f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
        return embed_code

    # If no video link is found, return the original content
    return content

@register.filter
def is_pdf(value):
    pdf_extensions = ['.pdf']
    return any(value.lower().endswith(ext) for ext in pdf_extensions)

@register.filter
def is_video_url(value):
    pattern = r'(?:https?://)?(?:www\.)?youtu(?:be\.com|\.be)(?:/watch\?v=|/embed/|/)([A-Za-z0-9_-]{11})'
    match = re.search(pattern, value)
    return match is not None

@register.filter
def split_paragraphs(value):
    # Split the content into sections based on paragraphs
    sections = re.split(r'\n\s*\n', value)
    return sections

