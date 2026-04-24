#!/usr/bin/env python3
"""
Create mug, shirt, tote bag, and phone case for a new design on ThePetParentStore.

Usage:
    python3 create_all_products.py <IMAGE_ID> <DESIGN_NAME>
    IMAGE_ID=xxx DESIGN_NAME=yyy python3 create_all_products.py

Design names must be in the DESCRIPTIONS dict below.
"""
import sys
import os
import json

# Add parent dir so we can import from printify/
sys.path.insert(0, os.path.dirname(__file__))
from printify.printify_api import api_request

# ─── Shop & shipping config (NEVER CHANGE) ───────────────────────────────────
SHOP_ID = 27174580

SHIPPING = {
    'mug':   303672859644,
    'shirt': 304014363208,
    'tote':  304118679662,
    'phone': 304115033514,
}

# ─── Etsy-optimised titles & descriptions ────────────────────────────────────
DESCRIPTIONS = {
    'dog_mom': {
        'title': 'Dog Mom Gift | Funny Dog Lover Mug Shirt Tote Phone Case | Gift for Dog Owner',
        'description': (
            "The perfect gift for the dog mom in your life! Whether she's obsessed with her pup "
            "or proudly calls herself a dog mom, this adorable design says it all.\n\n"
            "✅ Great for birthdays, Mother's Day, Christmas, or just because\n"
            "✅ Makes a thoughtful gift for dog lovers, rescue parents & fur mamas\n"
            "✅ Printed on demand — just for you!\n\n"
            "Show off your love for your four-legged family member with this cute, high-quality design."
        ),
    },
    'cat_mom': {
        'title': 'Cat Mom Gift | Funny Cat Lover Mug Shirt Tote Phone Case | Gift for Cat Owner',
        'description': (
            "Calling all cat moms! This purr-fect design is made for the proud cat parent who "
            "considers their kitty part of the family.\n\n"
            "✅ Great for birthdays, Mother's Day, holidays, or everyday gifting\n"
            "✅ Perfect for cat lovers, rescue parents & crazy cat ladies (proudly)\n"
            "✅ Printed on demand — just for you!\n\n"
            "Celebrate your bond with your feline family member in style."
        ),
    },
    'dog_dad': {
        'title': 'Dog Dad Gift | Funny Dog Lover Mug Shirt Tote Phone Case | Gift for Dog Owner',
        'description': (
            "For the proud dog dad who spoils his pup rotten — this design is all him.\n\n"
            "✅ Perfect for Father's Day, birthdays, Christmas & more\n"
            "✅ Ideal for dog lovers, rescue dads & fur dads everywhere\n"
            "✅ Printed on demand — just for you!\n\n"
            "Celebrate the bond between a man and his best friend."
        ),
    },
    'cat_dad': {
        'title': 'Cat Dad Gift | Funny Cat Lover Mug Shirt Tote Phone Case | Gift for Cat Owner',
        'description': (
            "For the cool cat dad who never misses a feeding time — this one's for him.\n\n"
            "✅ Perfect for Father's Day, birthdays, holidays & spontaneous gifting\n"
            "✅ Ideal for cat lovers, rescue dads & multi-cat household managers\n"
            "✅ Printed on demand — just for you!\n\n"
            "The cat chose him, and honestly that tracks."
        ),
    },
    'pet_parent': {
        'title': 'Pet Parent Gift | Funny Pet Lover Mug Shirt Tote Phone Case | Gift for Animal Lover',
        'description': (
            "For the pet parent who loves their fur baby more than most people — relatable.\n\n"
            "✅ Great for any occasion — birthday, holiday, or just because\n"
            "✅ Perfect for dog lovers, cat lovers, and all animal lovers\n"
            "✅ Printed on demand — just for you!\n\n"
            "Celebrate the unconditional love of pet parenthood."
        ),
    },
    'dog_lover': {
        'title': 'Dog Lover Gift | Cute Dog Mug Shirt Tote Phone Case | Gift for Dog Enthusiast',
        'description': (
            "Life is better with dogs — and this design makes sure everyone knows it.\n\n"
            "✅ Perfect for birthdays, holidays, and surprise gifts\n"
            "✅ Great for dog enthusiasts, breed fans, and shelter volunteers\n"
            "✅ Printed on demand — just for you!\n\n"
            "Because every dog deserves a human who shows their love out loud."
        ),
    },
    'cat_lover': {
        'title': 'Cat Lover Gift | Cute Cat Mug Shirt Tote Phone Case | Gift for Cat Enthusiast',
        'description': (
            "For the cat lover who has cat hair on every piece of clothing and zero regrets.\n\n"
            "✅ Perfect for birthdays, holidays, and 'just because' moments\n"
            "✅ Great for cat enthusiasts, breed fans, and shelter volunteers\n"
            "✅ Printed on demand — just for you!\n\n"
            "Wear your cat obsession proudly."
        ),
    },
}

# ─── Product builders ─────────────────────────────────────────────────────────

def build_mug(image_id, title, description):
    """Blueprint 457 | Provider 1 | Two-sided placement."""
    return {
        'title': f'{title} | 11oz Ceramic Coffee Mug',
        'description': description,
        'blueprint_id': 457,
        'print_provider_id': 1,
        'variants': [],           # Printify auto-selects when empty for mugs
        'print_areas': [
            {
                'variant_ids': [],  # populated below after variants fetch
                'placeholders': [
                    {
                        'position': 'front',
                        'images': [
                            {
                                'id': image_id,
                                'x': 0.233,
                                'y': 0.5,
                                'scale': 0.5,
                                'angle': 0,
                            }
                        ],
                    },
                    {
                        'position': 'back',
                        'images': [
                            {
                                'id': image_id,
                                'x': 0.767,
                                'y': 0.5,
                                'scale': 0.5,
                                'angle': 0,
                            }
                        ],
                    },
                ],
            }
        ],
        'shipping_template_id': SHIPPING['mug'],
    }


# Light-color keyword filter for shirts
SHIRT_LIGHT_COLORS = {'white', 'natural', 'ash', 'light blue', 'soft pink', 'heather grey'}
SHIRT_SIZES = {'s', 'm', 'l', 'xl', '2xl'}

def build_shirt(image_id, title, description, variants):
    """
    Blueprint 12 | Provider 29 | Front print only.
    Filter to light colors, S-2XL, max 100 variants.
    """
    filtered = []
    for v in variants:
        options = {k.lower(): str(val).lower() for k, val in v.get('options', {}).items()}
        color = options.get('color', '')
        size  = options.get('size', '')
        if color in SHIRT_LIGHT_COLORS and size in SHIRT_SIZES:
            filtered.append(v)
        if len(filtered) >= 100:
            break

    if not filtered:
        print('  ⚠️  No matching shirt variants found — using first 10 as fallback.')
        filtered = variants[:10]

    variant_ids = [v['id'] for v in filtered]

    return {
        'title': f'{title} | Unisex T-Shirt',
        'description': description,
        'blueprint_id': 12,
        'print_provider_id': 29,
        'variants': [{'id': vid, 'price': 2499, 'is_enabled': True} for vid in variant_ids],
        'print_areas': [
            {
                'variant_ids': variant_ids,
                'placeholders': [
                    {
                        'position': 'front',
                        'images': [
                            {
                                'id': image_id,
                                'x': 0.5,
                                'y': 0.38,
                                'scale': 0.72,
                                'angle': 0,
                            }
                        ],
                    }
                ],
            }
        ],
        'shipping_template_id': SHIPPING['shirt'],
    }


def build_tote(image_id, title, description):
    """Blueprint 77 | Provider 1."""
    return {
        'title': f'{title} | Canvas Tote Bag',
        'description': description,
        'blueprint_id': 77,
        'print_provider_id': 1,
        'variants': [],
        'print_areas': [
            {
                'variant_ids': [],
                'placeholders': [
                    {
                        'position': 'front',
                        'images': [
                            {
                                'id': image_id,
                                'x': 0.5,
                                'y': 0.45,
                                'scale': 0.75,
                                'angle': 0,
                            }
                        ],
                    }
                ],
            }
        ],
        'shipping_template_id': SHIPPING['tote'],
    }


def build_phone(image_id, title, description):
    """Blueprint 45 | Provider 27."""
    return {
        'title': f'{title} | Phone Case',
        'description': description,
        'blueprint_id': 45,
        'print_provider_id': 27,
        'variants': [],
        'print_areas': [
            {
                'variant_ids': [],
                'placeholders': [
                    {
                        'position': 'front',
                        'images': [
                            {
                                'id': image_id,
                                'x': 0.5,
                                'y': 0.5,
                                'scale': 0.75,
                                'angle': 0,
                            }
                        ],
                    }
                ],
            }
        ],
        'shipping_template_id': SHIPPING['phone'],
    }


# ─── Publish helper ───────────────────────────────────────────────────────────

PUBLISH_PAYLOAD = {
    'title':       True,
    'description': True,
    'images':      True,
    'variants':    True,
    'tags':        True,
    'keyFeatures': True,
    'shipping_template': True,
}

def create_and_publish(product_type, payload):
    print(f'\n[{product_type.upper()}] Creating product...')
    result = api_request('POST', f'/shops/{SHOP_ID}/products.json', payload)
    if not result:
        print(f'  ✗ Failed to create {product_type}.')
        return None

    product_id = result.get('id')
    print(f'  ✓ Created: {result.get("title")} (ID: {product_id})')

    print(f'  → Publishing to Etsy...')
    pub = api_request('POST', f'/shops/{SHOP_ID}/products/{product_id}/publish.json', PUBLISH_PAYLOAD)
    if pub is not None:
        print(f'  ✓ Published to Etsy.')
    else:
        print(f'  ⚠️  Publish call returned no data (may still be queued).')

    return product_id


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Accept args or env vars
    if len(sys.argv) >= 3:
        image_id    = sys.argv[1]
        design_name = sys.argv[2]
    else:
        image_id    = os.environ.get('IMAGE_ID', '').strip()
        design_name = os.environ.get('DESIGN_NAME', '').strip()

    if not image_id or not design_name:
        print('Usage: python3 create_all_products.py <IMAGE_ID> <DESIGN_NAME>')
        print('       IMAGE_ID=xxx DESIGN_NAME=yyy python3 create_all_products.py')
        sys.exit(1)

    if design_name not in DESCRIPTIONS:
        known = ', '.join(sorted(DESCRIPTIONS.keys()))
        raise ValueError(
            f'Unknown design name: "{design_name}"\n'
            f'Add it to DESCRIPTIONS or use one of: {known}'
        )

    info        = DESCRIPTIONS[design_name]
    title       = info['title']
    description = info['description']

    print(f'🐾 ThePetParentStore — Creating products for design: {design_name}')
    print(f'   Image ID : {image_id}')
    print(f'   Title    : {title[:60]}...')

    # Fetch shirt variants to filter
    print('\n[SHIRT] Fetching available variants...')
    shirt_variants_data = api_request(
        'GET', f'/catalog/blueprints/12/print_providers/29/variants.json'
    )
    shirt_variants = shirt_variants_data.get('variants', []) if shirt_variants_data else []
    if not shirt_variants:
        print('  ⚠️  Could not fetch shirt variants. Shirt will be skipped.')

    results = {}

    # Mug
    mug_payload = build_mug(image_id, title, description)
    results['mug'] = create_and_publish('mug', mug_payload)

    # Shirt (only if variants available)
    if shirt_variants:
        shirt_payload = build_shirt(image_id, title, description, shirt_variants)
        results['shirt'] = create_and_publish('shirt', shirt_payload)
    else:
        results['shirt'] = None

    # Tote
    tote_payload = build_tote(image_id, title, description)
    results['tote'] = create_and_publish('tote', tote_payload)

    # Phone case
    phone_payload = build_phone(image_id, title, description)
    results['phone'] = create_and_publish('phone', phone_payload)

    # Summary
    print('\n' + '═' * 50)
    print('✅ Done! Product IDs:')
    for ptype, pid in results.items():
        status = pid if pid else '✗ failed'
        print(f'   {ptype:<8}: {status}')
    print('═' * 50)


if __name__ == '__main__':
    main()
