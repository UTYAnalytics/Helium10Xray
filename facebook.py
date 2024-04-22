import  facebook_scraper as fs
# Define the post URL or user/page ID
page_id = "2176397672479592"  # This should be the page or user ID
post_id = "7458175737635066"  # This is the specific post ID

# Example URL construction (if needed for clarity)
post_url = f"https://www.facebook.com/{page_id}/posts/{post_id}"

# Load cookies from a file
cookies = 'www.facebook.com_cookies (2).json'  # Update this to the path where your cookies.json file is located

# Fetch posts using cookies for login
for post in fs.get_posts(post_urls=[post_url], cookies=cookies):
    print("Post:", post)
