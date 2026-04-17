import os, glob

for f in glob.glob('templates/**/*.html', recursive=True):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix the javascript interpolation that was broken by $ -> ₹ blind replacement
    fixed = content.replace('₹{', '${')
    
    # Optional: some Django expressions like ${{ total_revenue }} in dashboard might have been broken if it caught the first $
    # Let's fix Django template tags just in case
    fixed = fixed.replace('₹{{', '${{')
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(fixed)

print("Fixed templates.")
