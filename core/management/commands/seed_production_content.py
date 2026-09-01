import os
import shutil
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth.models import User

from booking.models import ServiceCategory, Service, BusinessHours
from shop.models import ProductCategory, Product
from blog.models import BlogCategory, BlogPost
from core.models import GalleryImage
from academy.models import CourseCategory, Course


class Command(BaseCommand):
    help = "Seeds all essential production data (Services, Shop Products, Blog Articles, Gallery, Business Hours) and synchronizes media assets."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Bolbash Production Content Seeding..."))

        # 1. Sync static images into MEDIA_ROOT
        source_dir = os.path.join(settings.BASE_DIR, 'static', 'images', 'hairbybolbash')
        media_root = settings.MEDIA_ROOT

        def copy_media(src_filename, subfolder):
            src_path = os.path.join(source_dir, src_filename)
            dest_dir = os.path.join(media_root, subfolder)
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, src_filename)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dest_path)
                return f"{subfolder}/{src_filename}"
            return None

        # 2. Seed Business Hours
        self.stdout.write("-> Seeding Business Hours...")
        hours_data = [
            (0, '09:00:00', '18:00:00', True),  # Monday
            (1, '09:00:00', '18:00:00', True),  # Tuesday
            (2, '09:00:00', '18:00:00', True),  # Wednesday
            (3, '09:00:00', '18:00:00', True),  # Thursday
            (4, '09:00:00', '18:00:00', True),  # Friday
            (5, '09:00:00', '18:00:00', True),  # Saturday
            (6, '12:00:00', '17:00:00', False), # Sunday
        ]
        for day, open_t, close_t, active in hours_data:
            BusinessHours.objects.update_or_create(
                day_of_week=day,
                defaults={
                    'opening_time': open_t,
                    'closing_time': close_t,
                    'is_active': active,
                }
            )

        # 3. Seed Service Categories & Services
        self.stdout.write("-> Seeding Services & Categories...")
        service_categories = [
            ('Hair Styling & Updos', 'hair-styling-updos', 'Expert hair styling, bespoke ponytails, updos, and cornrows.', 1),
            ('Wig Installation & Lace Melt', 'wig-installation-lace-melt', '100% invisible HD lace melts, 360 installs, and custom wig making.', 2),
            ('Hair Revamping & Treatment', 'hair-revamping-treatment', 'Complete wash, deep conditioning, bundle restoration, and bleaching.', 3),
            ('Nail Artistry & Extensions', 'nail-artistry-extensions', 'Luxury acrylic full sets, gel polish, manicures, and pedicures.', 4),
            ('Body Piercing & Beauty', 'body-piercing-beauty', 'Professional ear/nose piercings and beauty care.', 5),
        ]

        cat_map = {}
        for name, slug, desc, order in service_categories:
            cat, _ = ServiceCategory.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc, 'display_order': order}
            )
            cat_map[slug] = cat

        services_data = [
            {
                'id': 1,
                'name': 'Bespoke Bridal Hair Styling & Glamour',
                'slug': 'bespoke-bridal-hair-styling',
                'category': cat_map['hair-styling-updos'],
                'short_description': 'Signature bridal hair styling, veil fitting, and regal bridal party looks.',
                'description': 'Our flagship bridal experience. Includes styling trial consultation, scalp prep, luxury styling, and veil placement.',
                'price': Decimal('45000.00'),
                'duration': 120,
                'featured': True,
                'img': 'bridal_hair_1.jpg'
            },
            {
                'id': 2,
                'name': 'Luxury Sleek Ponytail & Updo',
                'slug': 'luxury-sleek-ponytail-updo',
                'category': cat_map['hair-styling-updos'],
                'short_description': 'Ultra-sleek high/low ponytails and editorial updos with natural edges.',
                'description': 'Flawless sleek styling using heat-protecting serums and high-hold wax for zero flyaways.',
                'price': Decimal('15000.00'),
                'duration': 75,
                'featured': False,
                'img': 'ponytail_updo_1.jpg'
            },
            {
                'id': 3,
                'name': '360 & Frontal Wig Installation (HD Melt)',
                'slug': '360-frontal-wig-installation-hd-melt',
                'category': cat_map['wig-installation-lace-melt'],
                'short_description': '100% seamless hairline melt with custom bleached knots and baby hairs.',
                'description': 'Our master frontal melt service. Includes knot bleaching, tinting, precision plucking, and invisible adhesive melting.',
                'price': Decimal('20000.00'),
                'duration': 90,
                'featured': True,
                'img': 'wig_installation_1.jpg'
            },
            {
                'id': 4,
                'name': 'Closure Wig Installation & Customization',
                'slug': 'closure-wig-installation-customization',
                'category': cat_map['wig-installation-lace-melt'],
                'short_description': 'Glueless or melted 4x4, 5x5, 6x6 closure wig installation with razor finish.',
                'description': 'Quick, protective, and ultra-natural closure installations tailored to your skin tone.',
                'price': Decimal('12000.00'),
                'duration': 60,
                'featured': False,
                'img': 'frontal_melt_1.jpg'
            },
            {
                'id': 5,
                'name': '360 Full Lace Wig Installation',
                'slug': '360-full-lace-wig-installation',
                'category': cat_map['wig-installation-lace-melt'],
                'short_description': 'Full perimeter perimeter lace installation for multi-parting and high ponytails.',
                'description': 'Total perimeter bonding for high ponytails, bun styling, and natural styling versatility.',
                'price': Decimal('25000.00'),
                'duration': 120,
                'featured': True,
                'img': 'wig_installation_2.jpg'
            },
            {
                'id': 6,
                'name': 'Custom Wig Making & Machine Construction',
                'slug': 'custom-wig-making-machine-construction',
                'category': cat_map['wig-installation-lace-melt'],
                'short_description': 'Bespoke machine-stitched wig crafted to your exact head measurements.',
                'description': 'Professional machine construction using ventilated mesh dome caps for maximum durability.',
                'price': Decimal('18000.00'),
                'duration': 180,
                'featured': False,
                'img': 'wig_making_custom_1.jpg'
            },
            {
                'id': 7,
                'name': 'Frontal Revamp & Lace Replacement',
                'slug': 'frontal-revamp-lace-replacement',
                'category': cat_map['wig-installation-lace-melt'],
                'short_description': 'Replace old/torn lace frontals with fresh HD lace on existing bundles.',
                'description': 'Revive your favorite wig by removing old balding lace and attaching a brand new frontal.',
                'price': Decimal('16000.00'),
                'duration': 90,
                'featured': False,
                'img': 'frontal_melt_2.jpg'
            },
            {
                'id': 8,
                'name': 'Luxury Hair Revamping, Washing & Treatment',
                'slug': 'luxury-hair-revamping-washing-treatment',
                'category': cat_map['hair-revamping-treatment'],
                'short_description': 'Deep conditioning, silicone gloss wash, detangling, and hot-comb press.',
                'description': 'Transform stiff, tangled, or dull human hair bundles back into silky, fragrant perfection.',
                'price': Decimal('10000.00'),
                'duration': 60,
                'featured': True,
                'img': 'hair_revamping_1.jpg'
            },
            {
                'id': 9,
                'name': 'Luxury Acrylic Nail Extensions & Gel Art',
                'slug': 'luxury-acrylic-nail-extensions-gel-art',
                'category': cat_map['nail-artistry-extensions'],
                'short_description': 'Full acrylic tip extensions with bespoke chrome, ombré, and 3D nail art.',
                'description': 'Long-lasting acrylic enhancement sculpted to perfection with French tips, ombré, or crystal art.',
                'price': Decimal('12000.00'),
                'duration': 75,
                'featured': True,
                'img': 'nail_extensions_1.jpg'
            },
            {
                'id': 10,
                'name': 'Spa Manicure & Cuticle Treatment',
                'slug': 'spa-manicure-cuticle-treatment',
                'category': cat_map['nail-artistry-extensions'],
                'short_description': 'Deep hand massage, exfoliating scrub, nail shaping, and gel polish.',
                'description': 'Revitalizing hand soak, dead skin exfoliation, cuticle nourishment, and gel coating.',
                'price': Decimal('6000.00'),
                'duration': 45,
                'featured': False,
                'img': 'pedicure_manicure_1.jpg'
            },
            {
                'id': 11,
                'name': 'Luxury Pedicure & Foot Scrub Spa',
                'slug': 'luxury-pedicure-foot-scrub-spa',
                'category': cat_map['nail-artistry-extensions'],
                'short_description': 'Callus removal, sea salt foot scrub, relaxing massage, and shiny gel topcoat.',
                'description': 'Ultimate foot pampering session that leaves soles soft, calluses removed, and toenails polished.',
                'price': Decimal('8000.00'),
                'duration': 60,
                'featured': False,
                'img': 'pedicure_manicure_2.jpg'
            },
            {
                'id': 12,
                'name': 'Professional Body & Facial Piercing',
                'slug': 'professional-body-facial-piercing',
                'category': cat_map['body-piercing-beauty'],
                'short_description': 'Sterile earlobe, helix, tragus, and nose piercing with surgical steel studs.',
                'description': 'Hygienic single-use needle piercing administered with sterilizing aftercare kit and jewelry.',
                'price': Decimal('5000.00'),
                'duration': 30,
                'featured': False,
                'img': 'body_piercing_1.jpg'
            }
        ]

        for s_data in services_data:
            img_rel = copy_media(s_data['img'], 'services')
            Service.objects.update_or_create(
                slug=s_data['slug'],
                defaults={
                    'name': s_data['name'],
                    'category': s_data['category'],
                    'short_description': s_data['short_description'],
                    'description': s_data['description'],
                    'price': s_data['price'],
                    'duration': s_data['duration'],
                    'featured': s_data['featured'],
                    'active': True,
                    'image': img_rel if img_rel else f"services/{s_data['img']}"
                }
            )

        # 4. Seed Shop Categories & Products
        self.stdout.write("-> Seeding Shop Categories & Products...")
        shop_categories = [
            ('Hair Care & Revamping', 'hair-care-revamping', 'Shampoos, conditioners, and oils for virgin hair bundles.', '✨', 1),
            ('Wig Adhesives & Essentials', 'wig-adhesives-essentials', 'Lace glues, melt bands, skin protectors, and removers.', '🧴', 2),
            ('Styling Tools & Brushes', 'styling-tools-brushes', 'Hot combs, wax sticks, paddle brushes, and satin bonnets.', '✂️', 3),
            ('Nails & Body Glamour', 'nails-body-glamour', 'Gel polishes, press-on nails, cuticle oils, and piercing studs.', '💅', 4),
        ]

        shop_cat_map = {}
        for name, slug, desc, icon, order in shop_categories:
            scat, _ = ProductCategory.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc, 'icon': icon, 'order': order, 'active': True}
            )
            shop_cat_map[slug] = scat

        shop_products = [
            {
                'name': 'Bolbash Silk Infusion Hair Revamping Serum',
                'slug': 'bolbash-silk-infusion-serum',
                'category': shop_cat_map['hair-care-revamping'],
                'short_description': 'Lightweight thermal gloss serum that eliminates frizz and restores shine.',
                'full_description': 'Formulated with argan oil and silk proteins, this non-greasy serum locks in moisture, shields hair from heat styling up to 450°F, and delivers mirror-like shine to raw human hair extensions.',
                'price': Decimal('8500.00'),
                'stock': 25,
                'featured': True,
                'img': 'hair_product_oil_1.jpg'
            },
            {
                'name': 'Bolbash Invisible Frontal Lace Holding Spray',
                'slug': 'bolbash-invisible-frontal-holding-spray',
                'category': shop_cat_map['wig-adhesives-essentials'],
                'short_description': 'Maximum hold quick-dry lace adhesive spray for humidity-resistant melts.',
                'full_description': 'Specially created for active lifestyles and tropical climates. Dries clear without sticky white residue, ensuring your HD lace remains melted all day long.',
                'price': Decimal('9500.00'),
                'stock': 30,
                'featured': True,
                'img': 'hair_product_spray_1.jpg'
            },
            {
                'name': 'Bolbash Edge Control & Taming Styling Wax',
                'slug': 'bolbash-edge-control-wax-stick',
                'category': shop_cat_map['styling-tools-brushes'],
                'short_description': '24-hour non-flaking edge control wax stick for sleek flyaways and hairline sculpting.',
                'full_description': 'Smooth down baby hairs and flyaways effortlessly with our lavender-infused edge control wax stick. Delivers pliable all-day control without build-up.',
                'price': Decimal('6000.00'),
                'stock': 40,
                'featured': True,
                'img': 'hair_product_wax_1.jpg'
            },
            {
                'name': 'Bolbash Organic Scalp Stimulating & Growth Oil',
                'slug': 'bolbash-scalp-stimulating-growth-oil',
                'category': shop_cat_map['hair-care-revamping'],
                'short_description': 'Nutrient-rich herbal botanical blend designed to strengthen edges and nourish scalp.',
                'full_description': 'Infused with rosemary, peppermint, castor, and jojoba oils. Calms tension after tight braid downs, revitalizes hair follicles, and promotes healthy edge regrowth.',
                'price': Decimal('7500.00'),
                'stock': 20,
                'featured': False,
                'img': 'hair_product_oil_1.jpg'
            }
        ]

        for p_data in shop_products:
            img_rel = copy_media(p_data['img'], 'shop/products')
            Product.objects.update_or_create(
                slug=p_data['slug'],
                defaults={
                    'name': p_data['name'],
                    'category': p_data['category'],
                    'short_description': p_data['short_description'],
                    'full_description': p_data['full_description'],
                    'price': p_data['price'],
                    'stock_quantity': p_data['stock'],
                    'is_active': True,
                    'is_featured': p_data['featured'],
                    'image': img_rel if img_rel else f"shop/products/{p_data['img']}"
                }
            )

        # 5. Seed Editorial Blog Articles
        self.stdout.write("-> Seeding Blog Articles & Editorial...")
        author = User.objects.filter(is_staff=True).first() or User.objects.first()

        blog_categories = [
            ('Hair Care & Maintenance', 'hair-care-maintenance', 'Preserving virgin hair bundles, washing routines, edge control, and avoiding shedding.'),
            ('Lace & Wig Artistry', 'lace-wig-artistry', 'Frontal melting tips, HD vs Swiss lace comparisons, and wig revival secrets.'),
            ('Bridal & Wedding Glam', 'bridal-wedding-glam', 'Hair timelines, engagement styles, veil attachments, and bridal party beauty coordination.'),
            ('Salon News & Trends', 'salon-news-trends', 'Latest announcements, styling trends, and insider beauty advice from Bolbash.'),
        ]

        bcat_map = {}
        for name, slug, desc in blog_categories:
            bcat, _ = BlogCategory.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc}
            )
            bcat_map[slug] = bcat

        articles = [
            {
                'title': 'How to Maintain Your Raw Virgin Hair & Frontal Melt at Home',
                'slug': 'how-to-maintain-raw-virgin-hair-frontal-melt',
                'category': bcat_map['hair-care-maintenance'],
                'excerpt': 'Learn the exact step-by-step nighttime routine, washing technique, and product combinations required to keep your frontal melt flawless and your raw bundles silky.',
                'is_featured': True,
                'img': 'frontal_melt_1.jpg',
                'content': """<h3>The Golden Rules of Frontal Care</h3>
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
<p>Even with pristine home care, a lace frontal naturally loosens as your biological hair grows out underneath. We recommend booking a professional frontal revamp and maintenance appointment at Bolbash Beauty Spot every 2 to 3 weeks to preserve both your hair and the longevity of your lace.</p>"""
            },
            {
                'title': 'The Ultimate Bridal Hair Preparation Guide: 6 Weeks to Your Big Day',
                'slug': 'ultimate-bridal-hair-preparation-guide',
                'category': bcat_map['bridal-wedding-glam'],
                'excerpt': 'Planning your wedding? Follow our comprehensive beauty timeline covering consultations, trial installations, and wedding morning hair prep.',
                'is_featured': False,
                'img': 'bridal_hair_1.jpg',
                'content': """<h3>Your Journey to Timeless Bridal Elegance</h3>
<p>Your wedding day is one of the most photographed moments of your lifetime. From the traditional engagement attire to the white wedding gown, your hair frames every emotion and every portrait. Achieving that effortlessly regal look requires strategic planning.</p>

<h3>6 Weeks Before: The Bridal Consultation & Hair Sourcing</h3>
<p>Book your initial bridal styling consultation at Bolbash Beauty Spot. Bring reference photos of your wedding dress neckline, accessories, and veil. Ensure your human hair bundles or custom frontal wig are ordered and inspected for quality.</p>

<h3>3 Weeks Before: The Hair Trial Session</h3>
<p>Never leave your bridal hairstyle to guesswork on wedding morning. During your styling trial, we test parting dimensions, volume balance, accessory pinning, and ensure the hair texture harmonizes with your makeup.</p>

<h3>1 Week Before: Final Prep & Revamp</h3>
<p>Wash, deep-treat, and bleach knots on your bridal wig. Get your manicure and pedicure done 2 days before the wedding so your hands are flawless for ring exchange close-ups.</p>

<h3>Wedding Morning: Stress-Free Radiance</h3>
<p>Wear a button-down or zippered silk robe so you do not have to pull clothing over your styled hair. Relax, sip champagne, and let our bridal glam team bring your dream look to life.</p>"""
            },
            {
                'title': 'HD Lace vs. Swiss Lace: Which One Gives the Truest Invisible Melt?',
                'slug': 'hd-lace-vs-swiss-lace-comparison',
                'category': bcat_map['lace-wig-artistry'],
                'excerpt': 'Understanding the crucial differences between High Definition (HD) film lace and traditional Swiss lace so you can choose the ideal frontal for your skin tone and lifestyle.',
                'is_featured': False,
                'img': 'wig_installation_1.jpg',
                'content': """<h3>The Evolution of Lace Technology</h3>
<p>Not all lace frontals are created equal. The material, thickness, and weave of the lace dictate how invisible the installation appears under direct camera flash and natural sunlight.</p>

<h3>1. High Definition (HD) Lace: The Film Standard</h3>
<p>HD lace is crafted from ultra-thin, royal film lace. Because the material is exceptionally delicate, it melts seamlessly into all skin complexions from very fair to rich dark chocolate tones. It is the premier choice for weddings, photoshoots, and high-profile events.</p>
<p><strong>Longevity:</strong> Because HD lace is razor-thin, it requires gentle handling and professional revamping every 2-3 weeks.</p>

<h3>2. Swiss Lace: The Resilient Everyday Classic</h3>
<p>Swiss lace is slightly thicker and considerably more durable than HD lace. While it requires careful knot bleaching and tinting to blend seamlessly, it withstands daily wear, frequent styling changes, and regular cleansing exceptionally well.</p>

<h3>The Stylist Verdict</h3>
<p>For one-off special events, photography, or bridal ceremonies, choose <strong>Real HD Lace</strong>. For active daily wear, commuting, and long-term wig longevity, <strong>Transparent Swiss Lace</strong> offers the optimal balance of durability and beauty.</p>"""
            },
            {
                'title': '5 Common Hair Care Mistakes Damaging Your Natural Edges Under Wigs',
                'slug': '5-mistakes-damaging-natural-edges-under-wigs',
                'category': bcat_map['hair-care-maintenance'],
                'excerpt': 'Protect your hairline while enjoying protective styling. Discover the top mistakes causing traction alopecia and how Bolbash stylists safeguard your natural hair.',
                'is_featured': False,
                'img': 'hair_product_wax_1.jpg',
                'content': """<h3>Protective Styling Should Actually Protect</h3>
<p>Wigs are celebrated as protective styles, but improper installation and careless removal can do the opposite. Here are the 5 most frequent mistakes to avoid:</p>

<ol class="list-decimal list-inside space-y-3 text-brand-neutral-700">
    <li><strong>Tight Braid Downs:</strong> Excessive tension along the temple follicles causes traction alopecia. Always insist on gentle, tension-free perimeter cornrows.</li>
    <li><strong>Applying Adhesive Directly to Biological Hair:</strong> Glue must only be placed on the skin in front of your natural hairline or on a protective silicone wig cap.</li>
    <li><strong>Ripping Off Lace Without Adhesive Remover:</strong> Pulling dry lace rips out baby hairs. Always saturate the perimeter with alcohol-free adhesive release oil.</li>
    <li><strong>Wearing Wet Hair Under Wigs:</strong> Trapping moisture under a wig creates a breeding ground for scalp bacteria and fungal infections.</li>
    <li><strong>Skipping Nightly Scalp Massages:</strong> Applying stimulating oils like Bolbash Growth Serum stimulates circulation and preserves follicle health.</li>
</ol>"""
            }
        ]

        for art in articles:
            img_rel = copy_media(art['img'], 'blog')
            BlogPost.objects.update_or_create(
                slug=art['slug'],
                defaults={
                    'title': art['title'],
                    'category': art['category'],
                    'author': author,
                    'excerpt': art['excerpt'],
                    'content': art['content'],
                    'featured_image': img_rel if img_rel else f"blog/{art['img']}",
                    'is_featured': art['is_featured'],
                    'status': BlogPost.STATUS_PUBLISHED,
                    'meta_title': art['title'],
                    'meta_description': art['excerpt'][:155]
                }
            )

        # 6. Seed Portfolio Gallery Images
        self.stdout.write("-> Seeding Gallery Images...")
        gallery_items = [
            ('Regal Bridal Hair Styling', 'BRIDAL', 'bridal_hair_1.jpg', 'Bespoke bridal styling and veil placement.'),
            ('Traditional Engagement Glam', 'BRIDAL', 'bridal_hair_2.jpg', 'Gele and coral bead traditional coordination.'),
            ('Sleek High Ponytail & Edges', 'HAIRSTYLES', 'ponytail_updo_1.jpg', 'Sleek ponytail with sculpted edges.'),
            ('Editorial Textured Updo', 'HAIRSTYLES', 'ponytail_updo_2.jpg', 'Glamorous textured updo for events.'),
            ('Invisible HD Frontal Lace Melt', 'WIG_MELT', 'frontal_melt_1.jpg', '100% skin-melted HD frontal installation.'),
            ('360 Full Lace Unit Install', 'WIG_MELT', 'wig_installation_1.jpg', 'Full perimeter custom wig installation.'),
            ('Custom Machine Wig Construction', 'WIG_MELT', 'wig_making_custom_1.jpg', 'Bespoke machine-made human hair unit.'),
            ('Silky Straight Bundle Revamping', 'TRANSFORMATION', 'hair_revamping_1.jpg', 'Silicone wash and bone straight press.'),
            ('Luxury Acrylic Nails & Gel Polish', 'EVENTS', 'nail_extensions_1.jpg', 'French ombré acrylic tips.'),
            ('Spa Pedicure & Foot Scrub', 'EVENTS', 'pedicure_manicure_1.jpg', 'Callus removal and revitalizing foot spa.'),
            ('Professional Earlobe & Nose Piercing', 'EVENTS', 'body_piercing_1.jpg', 'Hygienic surgical steel stud piercing.'),
            ('Luxe Lash Extensions & Glam', 'EVENTS', 'lash_extensions_1.jpg', 'Full volume mink lash extensions.'),
        ]

        for title, cat, img_name, caption in gallery_items:
            img_rel = copy_media(img_name, 'gallery')
            GalleryImage.objects.update_or_create(
                title=title,
                defaults={
                    'category': cat,
                    'caption': caption,
                    'image': img_rel if img_rel else f"gallery/{img_name}",
                    'is_active': True
                }
            )

        self.stdout.write(self.style.SUCCESS("All Bolbash Production Content successfully seeded!"))
