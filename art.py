"""
Here should be some custom ASCII art
"""

def banner():
    banner_file = 'data/default_banner.txt'
    with open(banner_file) as f:
        data = f.read()
    print (data)
