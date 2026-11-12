"""
Deep Research Consultant Agent
AI-powered expert consultation using Gemini 2.5 Pro
Generates comprehensive product recommendations and reports
"""
import os
import uuid
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Energy efficiency data (BEE Star ratings)
ENERGY_DATA = {
    "5_star": {"annual_savings_percent": 45, "description": "Most energy efficient"},
    "4_star": {"annual_savings_percent": 35, "description": "Very energy efficient"},
    "3_star": {"annual_savings_percent": 25, "description": "Moderately efficient"},
    "2_star": {"annual_savings_percent": 15, "description": "Below average efficiency"},
    "1_star": {"annual_savings_percent": 5, "description": "Basic efficiency"}
}

# Average electricity cost per unit in India
ELECTRICITY_COST_PER_UNIT = 8  # INR per kWh


class DeepResearchConsultant:
    
    def __init__(self):
        self.gemini_client = None
    
    def _get_gemini_client(self):
        """Initialize Gemini 2.5 Pro client"""
        if not self.gemini_client:
            try:
                from emergentintegrations.llm.chat import LlmChat
                emergent_key = os.environ.get('EMERGENT_MODEL_API_KEY') or os.environ.get('EMERGENT_LLM_KEY')
                
                self.gemini_client = LlmChat(
                    api_key=emergent_key,
                    system_message="You are an expert home appliance consultant for Aditya Retail, specializing in premium home appliances from brands like Bosch, Siemens, Electrolux, Hindware and other quality brands. You provide detailed, data-driven recommendations based on customer requirements. Your analysis should be thorough, practical, and focused on helping customers make informed decisions."
                ).with_model("gemini", "gemini-2.5-flash")
                
            except Exception as e:
                print(f"Error initializing Gemini client: {e}")
                return None
        return self.gemini_client
    
    async def get_matching_products(self, requirements: Dict[str, Any]) -> List[Dict]:
        """
        Fetch products matching customer requirements - SMART SELECTION
        Ensures coverage of all requested categories within budget
        """
        
        appliance_types = requirements.get('appliance_types', [])
        budget_min = requirements.get('budget_min', 0)
        budget_max = requirements.get('budget_max', 1000000)
        brand_preference = requirements.get('brand_preference', [])
        
        # Map user-friendly names to actual database categories
        category_map = {
            'refrigerator': 'Refrigerator',
            'washing_machine': 'Washing Machine',
            'dishwasher': 'Dishwasher',
            'oven': 'Oven',
            'microwave': 'Oven',  # Often grouped together
            'cooktop': 'Gas Hob',
            'hob': 'Gas Hob',
            'gas_hob': 'Gas Hob',
            'induction': 'Induction Hob',
            'induction_hob': 'Induction Hob',
            'chimney': 'Chimney',
            'hood': 'Chimney',
            'dryer': 'Washing Machine',
            'coffee_machine': 'Coffee Machine',
            'coffee': 'Coffee Machine',
            'air_fryer': 'Air Fryer',
            'mixer': 'Mixer Grinder',
            'mixer_grinder': 'Mixer Grinder'
        }
        
        # Get mapped categories
        requested_categories = []
        for appliance in appliance_types:
            normalized = appliance.lower().replace(' ', '_').replace('-', '_')
            mapped = category_map.get(normalized, appliance)
            if mapped not in requested_categories:
                requested_categories.append(mapped)
        
        print(f"[DeepResearch] Requested appliances: {appliance_types}")
        print(f"[DeepResearch] Mapped categories: {requested_categories}")
        print(f"[DeepResearch] Budget: ₹{budget_min:,} - ₹{budget_max:,}")
        
        selected_products = []
        out_of_budget_categories = []
        
        # Calculate STRICT budget per category
        num_categories = max(len(requested_categories), 1)
        # Use max budget divided by categories - this is the HARD LIMIT per category
        max_budget_per_category = budget_max / num_categories
        
        print(f"[DeepResearch] Max budget per category: ₹{max_budget_per_category:,.0f}")
        
        # Track remaining budget for smarter allocation
        remaining_total_budget = budget_max
        
        # For each requested category, find products STRICTLY within budget
        for category in requested_categories:
            # Build query for this category WITH PRICE FILTER (price > 0 to avoid bad data)
            query = {
                'category': {'$regex': f'^{category}$', '$options': 'i'},
                'price': {'$gt': 0, '$lte': min(max_budget_per_category, remaining_total_budget)}
            }
            
            # Add brand preference if specified
            if brand_preference and 'any' not in [b.lower() for b in brand_preference]:
                query['brand'] = {'$in': brand_preference}
            
            # Fetch products sorted by price descending (best within budget)
            category_products = await db.products.find(
                query, {'_id': 0}
            ).sort('price', -1).to_list(10)
            
            print(f"[DeepResearch] Category '{category}': Found {len(category_products)} products within budget")
            
            if category_products:
                # Take the best (most expensive) product that fits in budget
                product = category_products[0]
                product['_selected_for'] = category
                product['_within_budget'] = True
                selected_products.append(product)
                remaining_total_budget -= product.get('price', 0)
            else:
                # No products within budget - try without brand filter
                query_no_brand = {
                    'category': {'$regex': f'^{category}$', '$options': 'i'},
                    'price': {'$gt': 0, '$lte': min(max_budget_per_category, remaining_total_budget)}
                }
                category_products = await db.products.find(
                    query_no_brand, {'_id': 0}
                ).sort('price', -1).limit(5).to_list(5)
                
                if category_products:
                    product = category_products[0]
                    product['_selected_for'] = category
                    product['_within_budget'] = True
                    selected_products.append(product)
                    remaining_total_budget -= product.get('price', 0)
                else:
                    # Still no products - this category is OUT OF BUDGET
                    # Find the cheapest product in this category to show as "out of budget"
                    cheapest_query = {
                        'category': {'$regex': f'^{category}$', '$options': 'i'},
                        'price': {'$gt': 0}  # Exclude products with 0 price (bad data)
                    }
                    cheapest = await db.products.find(
                        cheapest_query, {'_id': 0}
                    ).sort('price', 1).limit(1).to_list(1)
                    
                    if cheapest:
                        product = cheapest[0]
                        product['_selected_for'] = category
                        product['_within_budget'] = False
                        product['_budget_warning'] = f"⚠️ Cheapest {category} (₹{product.get('price', 0):,}) exceeds your per-category budget of ₹{max_budget_per_category:,.0f}"
                        selected_products.append(product)
                        out_of_budget_categories.append(category)
        
        # Calculate total
        total_price = sum(p.get('price', 0) for p in selected_products)
        within_budget_total = sum(p.get('price', 0) for p in selected_products if p.get('_within_budget', True))
        
        print(f"[DeepResearch] Selected {len(selected_products)} products")
        print(f"[DeepResearch] Total: ₹{total_price:,} (Within budget: ₹{within_budget_total:,})")
        print(f"[DeepResearch] Out of budget categories: {out_of_budget_categories}")
        
        # Store budget analysis for the report
        for product in selected_products:
            product['_budget_analysis'] = {
                'total_budget': budget_max,
                'per_category_budget': max_budget_per_category,
                'is_over_total': total_price > budget_max,
                'over_by': max(0, total_price - budget_max)
            }
        
        print(f"[DeepResearch] Final selection: {len(selected_products)} products, Total: ₹{total_price:,}")
        
        return selected_products
    
    def calculate_energy_savings(self, product: Dict, usage_hours_per_day: float = 8) -> Dict:
        """Calculate annual energy savings for a product"""
        
        # Extract power consumption from specifications
        specs = product.get('specifications', {})
        power_watts = specs.get('power', specs.get('wattage', 0))
        
        # Try to extract from string if needed
        if isinstance(power_watts, str):
            import re
            match = re.search(r'(\d+)', power_watts)
            power_watts = int(match.group(1)) if match else 500  # Default
        elif not power_watts:
            # Default power consumption by category
            category = product.get('category', '').lower()
            if 'refrigerator' in category:
                power_watts = 150
            elif 'washing' in category:
                power_watts = 500
            elif 'dishwasher' in category:
                power_watts = 1800
            elif 'oven' in category:
                power_watts = 2000
            elif 'chimney' in category:
                power_watts = 200
            else:
                power_watts = 500
        
        # Calculate annual consumption
        daily_kwh = (power_watts * usage_hours_per_day) / 1000
        annual_kwh = daily_kwh * 365
        annual_cost = annual_kwh * ELECTRICITY_COST_PER_UNIT
        
        # Estimate star rating based on brand and efficiency features
        efficiency_features = str(product.get('highlights', [])).lower()
        if 'inverter' in efficiency_features or 'energy efficient' in efficiency_features:
            estimated_stars = 4
        elif product.get('brand', '').lower() in ['bosch', 'siemens']:
            estimated_stars = 4  # Premium brands typically have good efficiency
        else:
            estimated_stars = 3
        
        # Calculate savings compared to 1-star appliance
        savings_percent = ENERGY_DATA[f"{estimated_stars}_star"]['annual_savings_percent']
        baseline_cost = annual_cost / (1 - savings_percent/100)
        annual_savings = baseline_cost - annual_cost
        
        return {
            'estimated_stars': estimated_stars,
            'power_watts': power_watts,
            'daily_kwh': round(daily_kwh, 2),
            'annual_kwh': round(annual_kwh, 2),
            'annual_cost': round(annual_cost, 2),
            'estimated_annual_savings': round(annual_savings, 2),
            'efficiency_rating': ENERGY_DATA[f"{estimated_stars}_star"]['description']
        }
    
    async def generate_consultation_report(
        self,
        consultation_id: str,
        requirements: Dict[str, Any],
        products: List[Dict]
    ) -> Dict[str, Any]:
        """Generate comprehensive consultation report using Gemini"""
        
        gemini = self._get_gemini_client()
        if not gemini:
            return self._generate_fallback_report(requirements, products)
        
        # Prepare product data for AI analysis
        product_summaries = []
        for p in products[:15]:  # Limit to top 15 for AI analysis
            energy_data = self.calculate_energy_savings(p)
            product_summaries.append({
                'name': p.get('name'),
                'brand': p.get('brand'),
                'price': p.get('price'),
                'category': p.get('category'),
                'specifications': p.get('specifications', {}),
                'highlights': p.get('highlights', []),
                'energy_analysis': energy_data
            })
        
        # Build comprehensive prompt
        prompt = f"""
As an expert home appliance consultant, analyze the following customer requirements and available products to generate a comprehensive consultation report.

## CUSTOMER REQUIREMENTS:
- **Kitchen Size**: {requirements.get('kitchen_size', 'Medium')}
- **Kitchen Dimensions**: {requirements.get('kitchen_dimensions', 'Not specified')}
- **Budget Range**: ₹{requirements.get('budget_min', 0):,} - ₹{requirements.get('budget_max', 500000):,}
- **Family Size**: {requirements.get('family_size', '4')} members
- **Cooking Frequency**: {requirements.get('cooking_frequency', 'Daily')}
- **Appliances Needed**: {', '.join(requirements.get('appliance_types', ['General']))}
- **Priority Factors** (ranked): {', '.join(requirements.get('priority_factors', ['Quality', 'Price']))}
- **Brand Preferences**: {', '.join(requirements.get('brand_preference', ['Any']))}
- **Special Requirements**: {requirements.get('special_requirements', 'None')}
- **Energy Efficiency Priority**: {requirements.get('energy_priority', 'Important')}
- **Aesthetic Preference**: {requirements.get('aesthetic_preference', 'Modern')}

## AVAILABLE PRODUCTS:
{json.dumps(product_summaries, indent=2)}

## GENERATE A COMPREHENSIVE REPORT WITH:

1. **EXECUTIVE SUMMARY** (2-3 paragraphs)
   - Overview of recommendations
   - Key considerations based on requirements
   - Total estimated investment

2. **TOP RECOMMENDATIONS** (Top 3-5 products)
   For each product provide:
   - Product name and brand
   - Price
   - Why it's recommended (specific to customer's needs)
   - Key features matching their requirements
   - Pros and Cons
   - Energy efficiency rating and annual savings

3. **DETAILED COMPARISON TABLE**
   Compare top recommendations across:
   - Price
   - Energy Rating
   - Key Features
   - Best For (use case)

4. **ENERGY EFFICIENCY ANALYSIS**
   - Estimated annual electricity cost for each recommendation
   - Potential savings over 5 years
   - Environmental impact

5. **BUDGET BREAKDOWN**
   - Recommended products total
   - Installation costs (estimated)
   - Total investment
   - Value for money assessment

6. **INSTALLATION REQUIREMENTS**
   - Space requirements
   - Electrical requirements
   - Plumbing needs (if applicable)
   - Professional installation recommendations

7. **SPECIAL OFFERS & SAVINGS**
   - Current promotions applicable
   - Bundle discounts if buying multiple appliances
   - EMI options

8. **EXPERT TIPS**
   - Maintenance recommendations
   - Best practices for longevity
   - Warranty information

Format the response in clean, structured JSON with the following structure:
{{
  "executive_summary": "...",
  "top_recommendations": [...],
  "comparison_table": [...],
  "energy_analysis": {{...}},
  "budget_breakdown": {{...}},
  "installation_requirements": {{...}},
  "special_offers": {{...}},
  "expert_tips": [...]
}}
"""
        
        try:
            response = gemini.message(prompt)
            
            # Parse AI response
            report_data = self._parse_ai_response(response)
            
            # CRITICAL: Merge actual product data into recommendations
            # The AI provides analysis but we need real product details (images, prices, specs)
            ai_recommendations = report_data.get('top_recommendations', [])
            enhanced_recommendations = []
            
            for i, p in enumerate(products[:10]):  # Take all products (up to 10)
                energy = self.calculate_energy_savings(p)
                
                # Find matching AI recommendation if exists
                ai_rec = {}
                for rec in ai_recommendations:
                    if isinstance(rec, dict) and (
                        rec.get('name', '').lower() in p.get('name', '').lower() or
                        p.get('name', '').lower() in rec.get('name', '').lower()
                    ):
                        ai_rec = rec
                        break
                
                enhanced_rec = {
                    'id': p.get('id'),
                    'name': p.get('name'),
                    'brand': p.get('brand'),
                    'price': p.get('price', 0),
                    'category': p.get('category'),
                    'images': p.get('images', []),
                    'specifications': p.get('specifications', {}),
                    'highlights': p.get('highlights', [])[:5],
                    'energy_analysis': energy,
                    'recommendation_reason': ai_rec.get('why_recommended') or ai_rec.get('recommendation_reason') or f"Premium {p.get('brand')} {p.get('category')} - top choice for quality and reliability.",
                    'pros': ai_rec.get('pros', [f"Premium {p.get('brand')} quality", "Energy efficient", "Advanced features"]),
                    'cons': ai_rec.get('cons', ["Premium pricing"]),
                    # PRESERVE budget analysis fields from product selection
                    '_within_budget': p.get('_within_budget', True),
                    '_budget_warning': p.get('_budget_warning', ''),
                    '_budget_analysis': p.get('_budget_analysis', {})
                }
                enhanced_recommendations.append(enhanced_rec)
            
            # Calculate proper budget breakdown
            total_products = sum(r.get('price', 0) for r in enhanced_recommendations)
            
            report_data['top_recommendations'] = enhanced_recommendations
            report_data['consultation_id'] = consultation_id
            report_data['generated_at'] = datetime.now(timezone.utc).isoformat()
            report_data['requirements'] = requirements
            report_data['products_analyzed'] = len(products)
            report_data['budget_breakdown'] = {
                'products_total': total_products,
                'estimated_installation': min(15000, total_products * 0.02),
                'grand_total': total_products + min(15000, total_products * 0.02),
                'budget_requested': f"₹{requirements.get('budget_min', 0):,} - ₹{requirements.get('budget_max', 0):,}"
            }
            
            return report_data
            
        except Exception as e:
            print(f"Error generating AI report: {e}")
            return self._generate_fallback_report(requirements, products)
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response, handling both JSON and text formats"""
        
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        
        # Return as structured text if JSON parsing fails
        return {
            'executive_summary': response[:500] if len(response) > 500 else response,
            'full_report': response,
            'format': 'text'
        }
    
    def _generate_fallback_report(self, requirements: Dict, products: List[Dict]) -> Dict:
        """Generate a basic report without AI - includes images and specifications"""
        
        # Take all products (up to 10) to cover all requested categories
        recommendations = []
        for p in products[:10]:
            energy = self.calculate_energy_savings(p)
            recommendations.append({
                'id': p.get('id'),
                'name': p.get('name'),
                'brand': p.get('brand'),
                'price': p.get('price', 0),
                'category': p.get('category'),
                'images': p.get('images', []),
                'specifications': p.get('specifications', {}),
                'highlights': p.get('highlights', [])[:5],
                'energy_analysis': energy,
                'recommendation_reason': f"Premium {p.get('brand')} {p.get('category')} - excellent quality and reliability for your kitchen.",
                # PRESERVE budget analysis fields from product selection
                '_within_budget': p.get('_within_budget', True),
                '_budget_warning': p.get('_budget_warning', ''),
                '_budget_analysis': p.get('_budget_analysis', {})
            })
        
        total_price = sum(r.get('price', 0) for r in recommendations)
        installation_cost = min(20000, total_price * 0.02)
        
        return {
            'executive_summary': f"Based on your requirements for a {requirements.get('kitchen_size', 'medium')} kitchen with a budget of ₹{requirements.get('budget_min', 0):,} - ₹{requirements.get('budget_max', 0):,}, we have curated {len(recommendations)} premium appliances from our collection. Total investment: ₹{total_price:,}.",
            'top_recommendations': recommendations,
            'budget_breakdown': {
                'products_total': total_price,
                'estimated_installation': installation_cost,
                'grand_total': total_price + installation_cost,
                'budget_requested': f"₹{requirements.get('budget_min', 0):,} - ₹{requirements.get('budget_max', 0):,}"
            },
            'requirements': requirements,
            'format': 'fallback'
        }
    
    def generate_html_report(self, report_data: Dict) -> str:
        """Generate beautiful HTML report for email with product images, specs, and CTAs"""
        
        # Use STORE_URL env var for all customer-facing links so production
        # emails point to adityaretail.com, not the preview/dev environment.
        store_url = os.environ.get("STORE_URL", "https://adityaretail.com").rstrip("/")

        requirements = report_data.get('requirements', {})
        recommendations = report_data.get('top_recommendations', [])
        budget = report_data.get('budget_breakdown', {})
        customer_name = requirements.get('customer_name', 'Valued Customer')
        
        # Build recommendations HTML with images and specifications
        recommendations_html = ""
        for i, rec in enumerate(recommendations[:6], 1):  # Show up to 6 products
            price = rec.get('price', 0)
            energy_data = rec.get('energy_analysis', {})
            
            # Get product image - use 900x size and PNG format for email compatibility
            images = rec.get('images', [])
            product_image = 'https://via.placeholder.com/200x200?text=Product'
            if images:
                img_url = images[0]
                # Use smaller 900x images instead of 5120x to avoid redirect issues
                if '/5120x/' in img_url:
                    img_url = img_url.replace('/5120x/', '/900x/')
                # Convert webp to png for better email client compatibility
                if img_url.endswith('.webp'):
                    img_url = img_url.replace('.webp', '.png')
                product_image = img_url
            
            # Get specifications
            specs = rec.get('specifications', {})
            highlights = rec.get('highlights', [])
            
            # Build specs HTML
            specs_html = ""
            if specs:
                spec_items = list(specs.items())[:4]  # Show top 4 specs
                for key, value in spec_items:
                    specs_html += f'<span style="display: inline-block; background: #e5e7eb; padding: 4px 8px; border-radius: 4px; margin: 2px; font-size: 11px;">{key}: {value}</span>'
            
            # Build highlights HTML
            highlights_html = ""
            if highlights:
                for highlight in highlights[:3]:
                    highlights_html += f'<li style="color: #374151; font-size: 12px; margin-bottom: 4px;">✓ {highlight}</li>'
            
            # Product URL for Buy Now button
            product_id = rec.get('id', '')
            product_url = f"{store_url}/#/product/{product_id}" if product_id else store_url
            
            # Check if product is within budget
            is_within_budget = rec.get('_within_budget', True)
            budget_warning = rec.get('_budget_warning', '')
            
            # Budget warning banner
            budget_warning_html = ''
            if not is_within_budget:
                budget_warning_html = f'''
                <div style="background: #fef2f2; border: 1px solid #fecaca; padding: 10px; border-radius: 6px; margin-bottom: 15px;">
                    <span style="color: #dc2626; font-size: 12px; font-weight: bold;">⚠️ EXCEEDS BUDGET</span>
                    <p style="color: #991b1b; font-size: 11px; margin: 5px 0 0 0;">{budget_warning}</p>
                </div>
                '''
            
            recommendations_html += f"""
            <div style="background: #ffffff; border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid {'#fecaca' if not is_within_budget else '#e5e7eb'}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                {budget_warning_html}
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td width="140" valign="top" style="padding-right: 20px;">
                            <img src="{product_image}" alt="{rec.get('name', 'Product')}" style="width: 120px; height: 120px; object-fit: contain; border-radius: 8px; background: #f9fafb;">
                        </td>
                        <td valign="top">
                            <h3 style="color: #1f2937; margin: 0 0 8px 0; font-size: 16px;">#{i}. {rec.get('name', 'Product')}</h3>
                            <p style="color: #6b7280; margin: 0 0 8px 0; font-size: 13px;">
                                <strong>{rec.get('brand', 'N/A')}</strong> | {rec.get('category', 'N/A')}
                            </p>
                            <p style="font-size: 22px; font-weight: bold; color: {'#dc2626' if not is_within_budget else '#2563eb'}; margin: 0 0 8px 0;">₹{price:,}</p>
                            <div style="margin-bottom: 8px;">
                                {specs_html}
                            </div>
                        </td>
                    </tr>
                </table>
                
                <!-- Highlights -->
                {f'<ul style="margin: 12px 0; padding-left: 20px;">{highlights_html}</ul>' if highlights_html else ''}
                
                <!-- Energy & Savings -->
                <div style="display: flex; gap: 10px; margin: 12px 0; flex-wrap: wrap;">
                    <div style="background: #fef3c7; padding: 6px 12px; border-radius: 6px;">
                        <span style="color: #92400e; font-size: 12px;">⚡ {energy_data.get('estimated_stars', 3)} Star Rating*</span>
                    </div>
                    <div style="background: #dbeafe; padding: 6px 12px; border-radius: 6px;">
                        <span style="color: #1e40af; font-size: 12px;">💰 Est. Energy Cost: ₹{energy_data.get('annual_cost', 0):,.0f}/yr*</span>
                    </div>
                    <div style="background: #d1fae5; padding: 6px 12px; border-radius: 6px;">
                        <span style="color: #065f46; font-size: 12px;">💡 Est. Savings: ₹{energy_data.get('estimated_annual_savings', 0):,.0f}/yr*</span>
                    </div>
                </div>
                
                <!-- Why Recommended -->
                <p style="color: #374151; font-size: 13px; margin: 10px 0; background: #f0fdf4; padding: 10px; border-radius: 6px;">
                    <strong>Why Recommended:</strong> {rec.get('recommendation_reason', 'Excellent match for your requirements')}
                </p>
                
                <!-- Product CTA -->
                <div style="margin-top: 12px;">
                    <a href="{product_url}" style="display: inline-block; background: #2563eb; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 13px; margin-right: 8px;">🛒 Buy Now</a>
                    <a href="https://wa.me/919844577440?text=Hi,%20I'm%20interested%20in%20{rec.get('name', 'this product').replace(' ', '%20')}" style="display: inline-block; background: #25d366; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 13px;">💬 WhatsApp</a>
                </div>
            </div>
            """
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f3f4f6; margin: 0; padding: 20px;">
    <div style="max-width: 700px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); padding: 40px 30px; text-align: center;">
            <h1 style="color: white; margin: 0 0 10px 0; font-size: 28px;">🏠 Expert Consultation Report</h1>
            <p style="color: #bfdbfe; margin: 0; font-size: 16px;">Personalized Appliance Recommendations for {customer_name}</p>
        </div>
        
        <!-- Customer Info -->
        <div style="background: #eff6ff; padding: 20px 30px; border-bottom: 1px solid #dbeafe;">
            <h2 style="color: #1e40af; margin: 0 0 15px 0; font-size: 18px;">📋 Your Requirements</h2>
            <table width="100%" cellpadding="5">
                <tr>
                    <td><strong>Kitchen Size:</strong> {requirements.get('kitchen_size', 'Medium')}</td>
                    <td><strong>Budget:</strong> ₹{requirements.get('budget_min', 0):,} - ₹{requirements.get('budget_max', 0):,}</td>
                </tr>
                <tr>
                    <td><strong>Family Size:</strong> {requirements.get('family_size', '4')} members</td>
                    <td><strong>Cooking:</strong> {requirements.get('cooking_frequency', 'Daily')}</td>
                </tr>
                <tr>
                    <td><strong>Brands:</strong> {', '.join(requirements.get('brand_preference', ['Any']))}</td>
                    <td><strong>Appliances:</strong> {', '.join(requirements.get('appliance_types', []))[:50]}</td>
                </tr>
            </table>
        </div>
        
        <!-- Executive Summary -->
        <div style="padding: 30px;">
            <h2 style="color: #1f2937; margin: 0 0 15px 0; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">📊 Executive Summary</h2>
            <p style="color: #4b5563; line-height: 1.7;">{report_data.get('executive_summary', 'Based on your requirements, we have curated the best appliances for your kitchen.')}</p>
        </div>
        
        <!-- Recommendations -->
        <div style="padding: 0 30px 30px;">
            <h2 style="color: #1f2937; margin: 0 0 20px 0; border-bottom: 2px solid #10b981; padding-bottom: 10px;">⭐ Top Recommendations</h2>
            {recommendations_html}
        </div>
        
        <!-- Budget Summary -->
        <div style="background: #f0fdf4; padding: 30px; margin: 0 30px 30px; border-radius: 12px;">
            <h2 style="color: #065f46; margin: 0 0 20px 0;">💰 Budget Summary</h2>
            <table width="100%" cellpadding="8">
                <tr>
                    <td style="color: #374151;">Products Total:</td>
                    <td style="text-align: right; font-weight: bold; color: #1f2937;">₹{budget.get('products_total', 0):,}</td>
                </tr>
                <tr>
                    <td style="color: #374151;">Est. Installation:</td>
                    <td style="text-align: right; font-weight: bold; color: #1f2937;">₹{budget.get('estimated_installation', 5000):,}</td>
                </tr>
                <tr>
                    <td style="color: #6b7280; font-size: 13px;">Your Budget:</td>
                    <td style="text-align: right; color: #6b7280; font-size: 13px;">{budget.get('budget_requested', 'N/A')}</td>
                </tr>
                <tr style="border-top: 2px solid #a7f3d0;">
                    <td style="color: #065f46; font-size: 18px; font-weight: bold; padding-top: 12px;">Grand Total:</td>
                    <td style="text-align: right; font-size: 24px; font-weight: bold; color: {'#dc2626' if budget.get('products_total', 0) > requirements.get('budget_max', float('inf')) else '#059669'}; padding-top: 12px;">₹{budget.get('grand_total', 0):,}</td>
                </tr>
            </table>
            {'<p style="color: #dc2626; font-size: 13px; margin-top: 15px; padding: 10px; background: #fef2f2; border-radius: 6px;">⚠️ <strong>Note:</strong> Total exceeds your budget. Our sales team can help you find alternatives or discuss financing options.</p>' if budget.get('products_total', 0) > requirements.get('budget_max', float('inf')) else ''}
        </div>
        
        <!-- INSTANT HELP BANNER -->
        <div style="background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%); padding: 25px 30px; margin: 0 30px 30px; border-radius: 12px; text-align: center;">
            <h3 style="color: white; margin: 0 0 10px 0; font-size: 18px;">💬 Need Instant Help?</h3>
            <p style="color: #ddd6fe; margin: 0 0 15px 0; font-size: 14px;">Chat with our Sales Expert right now for personalized assistance</p>
            <a href="{store_url}/#/chat-sales" style="display: inline-block; background: white; color: #7c3aed; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 15px;">🤖 Chat with AI Sales Agent</a>
        </div>
        
        <!-- CTA Section -->
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #1f2937 0%, #111827 100%);">
            <h3 style="color: white; margin: 0 0 8px 0; font-size: 22px;">Ready to Transform Your Kitchen?</h3>
            <p style="color: #9ca3af; margin: 0 0 20px 0; font-size: 14px;">Our experts are here to help you make the right choice</p>
            
            <div style="margin-bottom: 20px;">
                <a href="tel:+919844577440" style="display: inline-block; background: #10b981; color: white; padding: 14px 30px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; margin: 5px;">📞 Call Now</a>
                <a href="https://wa.me/919844577440?text=Hi,%20I%20received%20my%20consultation%20report%20and%20would%20like%20to%20discuss%20my%20requirements" style="display: inline-block; background: #25d366; color: white; padding: 14px 30px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; margin: 5px;">💬 WhatsApp Us</a>
            </div>
            
            <a href="{store_url}" style="display: inline-block; background: #2563eb; color: white; padding: 14px 40px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">🛒 Shop All Products</a>
            
            <p style="color: #6b7280; margin: 20px 0 0 0; font-size: 13px;">
                📍 Visit us: Aditya Retail, Bangalore<br>
                📧 Email: online.adityaretail@gmail.com | 📱 +91 98445 77440
            </p>
        </div>
        
        <!-- Disclaimer -->
        <div style="background: #fef3c7; padding: 15px 30px; border-top: 1px solid #fcd34d;">
            <p style="color: #92400e; font-size: 11px; margin: 0; line-height: 1.6;">
                <strong>* Disclaimer:</strong> Energy ratings, annual energy costs, and savings estimates are approximate calculations based on typical usage patterns and average electricity rates (₹8/kWh). 
                Actual values may vary based on your usage, local electricity rates, and product specifications. Please refer to the official BEE star rating label on the product for certified energy efficiency information.
                Prices are subject to change. Installation charges may vary based on location and requirements.
            </p>
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; padding: 20px; background: #f9fafb; color: #6b7280; font-size: 12px;">
            <p style="margin: 0;">This report was generated by Aditya Retail's AI Expert Consultant</p>
            <p style="margin: 5px 0 0 0;">© 2024 Aditya Retail - Premium Home Appliances | Authorized Bosch & Siemens Dealer</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    async def send_consultation_report(
        self,
        consultation_id: str,
        email: str,
        report_data: Dict
    ) -> bool:
        """Send consultation report via email"""
        
        try:
            from sendgrid_email_service import sendgrid_email_service
            
            print(f"[DeepResearch] Generating HTML report for consultation {consultation_id}")
            html_report = self.generate_html_report(report_data)
            customer_name = report_data.get('requirements', {}).get('customer_name', 'Valued Customer')
            
            print(f"[DeepResearch] Sending email to {email} for customer {customer_name}")
            print(f"[DeepResearch] HTML report length: {len(html_report)} chars")
            
            result = sendgrid_email_service.send_email(
                to_email=email,
                subject="🏠 Your Expert Kitchen Consultation Report is Ready!",
                body=html_report,
                from_agent="consultant",
                html=True
            )
            
            print(f"[DeepResearch] Email send result: {result}")
            
            if result.get('status') == 'success':
                print(f"[DeepResearch] ✅ Email sent successfully to {email}")
                return True
            else:
                print(f"[DeepResearch] ❌ Email failed: {result.get('message', 'Unknown error')}")
                return False
            
        except Exception as e:
            import traceback
            print(f"[DeepResearch] ❌ Error sending consultation report: {e}")
            print(f"[DeepResearch] Traceback: {traceback.format_exc()}")
            return False
    
    async def process_consultation_request(
        self,
        consultation_id: str,
        requirements: Dict[str, Any]
    ) -> Dict:
        """Main method to process a consultation request"""
        
        try:
            # Update status to processing
            await db.consultations.update_one(
                {"id": consultation_id},
                {"$set": {"status": "processing", "processing_started_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            # Get matching products
            products = await self.get_matching_products(requirements)
            
            if not products:
                # Expand search if no products found
                expanded_req = {**requirements}
                expanded_req['budget_max'] = requirements.get('budget_max', 200000) * 1.5
                products = await self.get_matching_products(expanded_req)
            
            # Generate AI report
            report_data = await self.generate_consultation_report(
                consultation_id,
                requirements,
                products
            )
            
            # Send email
            email = requirements.get('email')
            email_sent = False
            if email:
                email_sent = await self.send_consultation_report(
                    consultation_id,
                    email,
                    report_data
                )
            
            # Update consultation record
            await db.consultations.update_one(
                {"id": consultation_id},
                {
                    "$set": {
                        "status": "completed",
                        "completed_at": datetime.now(timezone.utc).isoformat(),
                        "report": report_data,
                        "email_sent": email_sent,
                        "products_matched": len(products)
                    }
                }
            )
            
            return {
                "status": "success",
                "consultation_id": consultation_id,
                "products_analyzed": len(products),
                "email_sent": email_sent,
                "report": report_data
            }
            
        except Exception as e:
            print(f"Error processing consultation: {e}")
            
            await db.consultations.update_one(
                {"id": consultation_id},
                {
                    "$set": {
                        "status": "failed",
                        "error": str(e),
                        "failed_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            return {"status": "error", "message": str(e)}


# Global instance
deep_research_consultant = DeepResearchConsultant()
