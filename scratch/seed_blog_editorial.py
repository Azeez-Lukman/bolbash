import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from blog.models import BlogCategory, BlogPost


def seed_blog():
    print("Seeding Bolbash Beauty Spot Editorial & Blog...")

    # Author
    author = User.objects.filter(is_staff=True).first()
    if not author:
        author = User.objects.first()

    # 1. Categories
    categories_data = [
        {
            "name": "Hair Care & Maintenance",
            "slug": "hair-care-maintenance",
            "description": "Essential guidance on preserving virgin hair bundles, washing routines, edge control, and avoiding shedding."
        },
        {
            "name": "Lace & Wig Artistry",
            "slug": "lace-wig-artistry",
            "description": "Frontal melting tips, HD vs Swiss lace comparisons, glueless customization, and wig revival secrets."
        },
        {
            "name": "Bridal & Wedding Glam",
            "slug": "bridal-wedding-glam",
            "description": "Hair preparation timelines, traditional engagement styles, veil attachments, and bridal party beauty coordination."
        },
        {
            "name": "Salon News & Trends",
            "slug": "salon-news-trends",
            "description": "Latest announcements, seasonal promotions, styling trends, and insider beauty advice from Bolbash."
        }
    ]

    categories = {}
    for cat_data in categories_data:
        cat, created = BlogCategory.objects.get_or_create(
            slug=cat_data["slug"],
            defaults={
                "name": cat_data["name"],
                "description": cat_data["description"]
            }
        )
        categories[cat_data["slug"]] = cat
        print(f"  - Category: {cat.name} ({'Created' if created else 'Existing'})")

    # 2. Articles
    articles_data = [
        {
            "title": "How to Maintain Your Raw Virgin Hair & Frontal Melt at Home",
            "slug": "how-to-maintain-raw-virgin-hair-frontal-melt",
            "category": categories["hair-care-maintenance"],
            "excerpt": "Learn the exact step-by-step nighttime routine, washing technique, and product combinations required to keep your frontal melt flawless and your raw bundles silky.",
            "is_featured": True,
            "content": """<h3>The Golden Rules of Frontal Care</h3>
<p>A flawless frontal melt is an investment in your confidence and beauty. When done by a master stylist, the lace disappears seamlessly into your skin. However, what you do in the days and weeks following your appointment determines how long that seamless melt endures.</p>

<div class="my-6 p-6 rounded-2xl bg-brand-pink/10 border-l-4 border-brand-pink space-y-2">
    <h4 class="font-heading font-bold text-brand-black text-base">Key Maintenance Essentials:</h4>
    <ul class="list-disc list-inside space-y-1 text-sm text-brand-neutral-700">
        <li>Always tie your hairline with a satin/silk melt band before taking a shower or exercising.</li>
        <li>Never apply heavy, alcohol-based gels directly to delicate HD lace.</li>
        <li>Detangle gently from ends to roots using a flexible paddle brush.</li>
    </ul>
</div>

<h3>1. Nighttime Protection: Your Satin Wrap Routine</h3>
<p>Friction during sleep is the number one cause of premature lace lifting, hair breakage, and tangles. Never go to sleep without properly wrapping your hair. Apply an elastic satin melt band around your frontal perimeter, and tuck your lengths into a premium silk bonnet.</p>

<h3>2. Washing Raw Human Hair Without Shedding</h3>
<p>When cleansing raw human hair extensions, lukewarm water and sulfate-free hydrating shampoo are mandatory. Gently work the shampoo downwards from roots to ends without scrubbing or balling the hair up. Follow with a rich moisture conditioner, allowing it to penetrate for at least 15 minutes before rinsing with cool water to seal the hair cuticles.</p>

<h3>3. Managing Sweat and Humidity</h3>
<p>In warm climates, sweat can react with adhesives. If you feel moisture accumulating along your hairline after a workout, do not scratch or pull at the lace. Blot gently with a clean microfibre towel and tie your melt band firmly for 15 minutes until dry.</p>

<h3>When to Visit the Salon for a Revamp</h3>
<p>Even with pristine home care, a lace frontal naturally loosens as your biological hair grows out underneath. We recommend booking a professional frontal revamp and maintenance appointment at Bolbash Beauty Spot every 2 to 3 weeks to preserve both your hair and the longevity of your lace.</p>""",
            "meta_title": "How to Maintain Your Raw Virgin Hair & Frontal Melt | Bolbash Beauty",
            "meta_description": "Discover master tips on protecting your frontal melt, washing human hair extensions, and avoiding lace lifting from Bolbash stylists in Ibadan."
        },
        {
            "title": "The Ultimate Bridal Hair Preparation Guide: 6 Weeks to Your Big Day",
            "slug": "ultimate-bridal-hair-preparation-guide",
            "category": categories["bridal-wedding-glam"],
            "excerpt": "Planning your wedding? Follow our comprehensive beauty timeline covering consultations, trial installations, and wedding morning hair prep.",
            "is_featured": False,
            "content": """<h3>Your Journey to Timeless Bridal Elegance</h3>
<p>Your wedding day is one of the most photographed moments of your lifetime. From the traditional engagement attire to the white wedding gown, your hair frames every emotion and every portrait. Achieving that effortlessly regal look requires strategic planning.</p>

<h3>6 Weeks Out: The Bridal Consultation</h3>
<p>Book your initial bridal consultation at Bolbash Beauty Spot. Bring reference photos of your gown neckline, your veil style, and your dream hairstyle. This is the stage where we evaluate whether your desired look requires custom-tailored wig construction, clip-ins, or natural hair sculpting.</p>

<h3>4 Weeks Out: Hair Sourcing & Custom Coloring</h3>
<p>If your bridal look involves a custom luxury wig or raw human hair bundles, this is the time to finalize sourcing, custom bleaching, and tone matching. Never experiment with drastic new hair dyes during the week of your wedding.</p>

<h3>2 Weeks Out: Trial Run & Veil Attachment Test</h3>
<p>During the bridal trial, our master stylists create the complete look, securing your tiara, traditional coral beads, or cathedral veil. We test the hold, weight distribution, and comfort so you can dance with total confidence on your big day.</p>

<h3>The Morning of the Wedding</h3>
<p>Relax and let our dedicated bridal glam team take over. Ensure your hair or skin is cleansed and product-free as instructed during your trial. Our mobile bridal team ensures seamless on-location styling for you and your bridal train.</p>""",
            "meta_title": "Bridal Hair Preparation Guide: 6 Weeks to Your Wedding | Bolbash",
            "meta_description": "Step-by-step bridal hair preparation timeline for Nigerian brides. Master consultations, trial runs, and wedding morning hair styling."
        },
        {
            "title": "5 Clear Signs Your Human Hair Wig Needs a Professional Revamp",
            "slug": "5-signs-your-wig-needs-professional-revamp",
            "category": categories["lace-wig-artistry"],
            "excerpt": "Before you think about discarding your favorite wig, check these 5 indicators. A professional deep detox, closure replacement, and revamping can restore it like new.",
            "is_featured": False,
            "content": """<h3>Don't Throw Away Tired Wigs — Revamp Them</h3>
<p>High-quality raw and virgin human hair wigs are built to last for years when maintained properly. However, accumulated styling products, heat damage, and friction can leave hair looking stiff, lifeless, or tangled. Here is how to know when your wig is due for our signature revitalization treatment.</p>

<h3>1. Persistent Stiffness and Loss of Natural Bounce</h3>
<p>If your wig feels crunchy or stiff even after at-home conditioning, product build-up and mineral deposits have coated the hair cuticles. A professional clarifying steam detox is required to strip the buildup without stripping natural moisture.</p>

<h3>2. The Lace Closure is Balding or Thinning</h3>
<p>Over-plucking, high-tension brushing, or repeated re-installs can cause thinning at the lace parting. At Bolbash Beauty Spot, our revamping service includes precision closure and frontal replacements, seamlessly matching your existing bundle textures.</p>

<h3>3. Stubborn Tangles at the Nape</h3>
<p>When the nape area constantly knots together within hours of brushing, the cuticles have become dry and misaligned. Our deep conditioning reconstructive baths smooth the cuticles back into place.</p>

<h3>4. Dull, Faded Color</h3>
<p>Sunlight exposure and washing cause dark tones to fade into brassy browns. A professional toner bath and gloss treatment restores rich, mirror-like obsidian shine.</p>

<h3>5. Loose or Deconstructed Cap Foundation</h3>
<p>An ill-fitting wig cap causes frontal slippage and bumps. We re-size, re-sew loose tracks, and replace worn elastic bands so your unit fits like a tailored glove.</p>""",
            "meta_title": "5 Signs Your Wig Needs Professional Revamping | Bolbash Beauty",
            "meta_description": "Learn how professional wig revamping, deep detoxing, and closure replacement can restore your expensive human hair wigs to brand-new condition."
        },
        {
            "title": "HD Lace vs Swiss Lace: Which Frontal is Best for Your Skin Tone?",
            "slug": "hd-lace-vs-swiss-lace-guide",
            "category": categories["lace-wig-artistry"],
            "excerpt": "Confused between High Definition (HD) lace and transparent Swiss lace? We break down the durability, melt transparency, and maintenance differences.",
            "is_featured": False,
            "content": """<h3>Decoding Lace Types for Flawless Melts</h3>
<p>The foundation of any breathtaking wig installation lies in the quality of the lace. With so many terms on the market—HD, Swiss, Transparent, French—it is easy to feel overwhelmed. Here is everything you need to know to make the best choice for your lifestyle and budget.</p>

<h3>What is HD Lace?</h3>
<p>HD (High Definition) lace is an ultra-thin, delicate royal lace film that is almost invisible to the naked eye. When tinted correctly and installed with our signature melt technique, it blends seamlessly into all skin complexions with zero visible grid lines.</p>
<p><strong>Best For:</strong> Weddings, photo shoots, special events, and clients who prioritize absolute invisibility.</p>
<p><strong>Note:</strong> Because it is ultra-fine, HD lace requires gentler handling and lighter tension when brushing.</p>

<h3>What is Transparent Swiss Lace?</h3>
<p>Swiss lace is slightly thicker than HD lace, offering greater durability and resistance to tearing while still providing an excellent melt when bleached and tinted to match your skin undertones.</p>
<p><strong>Best For:</strong> Daily everyday wear, high-activity lifestyles, and budget-conscious beauty enthusiasts seeking long-lasting resilience.</p>

<h3>How Bolbash Stylists Match Your Perfect Melt</h3>
<p>During every salon installation, our stylists customize your lace knots with precision bleaching, plucking, and bespoke skin-tone tinting. Book an appointment today and experience the Bolbash difference!</p>""",
            "meta_title": "HD Lace vs Swiss Lace: Frontal Comparison Guide | Bolbash",
            "meta_description": "Understand the differences between HD lace and Swiss lace frontals for the most natural melt and long-lasting wig installations."
        }
    ]

    for art_data in articles_data:
        post, created = BlogPost.objects.get_or_create(
            slug=art_data["slug"],
            defaults={
                "title": art_data["title"],
                "category": art_data["category"],
                "author": author,
                "excerpt": art_data["excerpt"],
                "content": art_data["content"],
                "status": BlogPost.STATUS_PUBLISHED,
                "is_featured": art_data["is_featured"],
                "published_at": timezone.now(),
                "meta_title": art_data["meta_title"],
                "meta_description": art_data["meta_description"]
            }
        )
        print(f"  - Post: {post.title} ({'Created' if created else 'Existing'})")

    print("Editorial seed completed successfully!")


if __name__ == '__main__':
    seed_blog()
