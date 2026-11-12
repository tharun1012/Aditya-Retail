"""
ROI Calculator Service
Comprehensive store ROI analysis, pre-feasibility, and breakeven calculations
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Industry Benchmarks for Home Appliance Retail
INDUSTRY_BENCHMARKS = {
    "rent_to_revenue_ratio": {
        "tier_1_city": {"min": 0.06, "max": 0.10, "recommended": 0.08},  # 6-10% of revenue
        "tier_2_city": {"min": 0.04, "max": 0.07, "recommended": 0.05},
        "tier_3_city": {"min": 0.03, "max": 0.05, "recommended": 0.04}
    },
    "staff_cost_ratio": 0.08,  # 8% of revenue
    "utilities_ratio": 0.02,   # 2% of revenue
    "marketing_ratio": 0.03,   # 3% of revenue
    "misc_expenses_ratio": 0.02,  # 2% of revenue
    
    "gross_margins": {
        "washing-machine": {"min": 0.15, "max": 0.22, "avg": 0.18},
        "refrigerator": {"min": 0.14, "max": 0.20, "avg": 0.17},
        "chimney": {"min": 0.20, "max": 0.30, "avg": 0.25},
        "gas-hob": {"min": 0.18, "max": 0.25, "avg": 0.22},
        "dishwasher": {"min": 0.16, "max": 0.24, "avg": 0.20},
        "oven": {"min": 0.18, "max": 0.26, "avg": 0.22},
        "microwave": {"min": 0.15, "max": 0.22, "avg": 0.18},
        "sink": {"min": 0.25, "max": 0.35, "avg": 0.30},
        "default": {"min": 0.15, "max": 0.25, "avg": 0.20}
    },
    
    "revenue_per_sqft": {
        "tier_1_city": {"min": 800, "max": 1500, "avg": 1100},  # Monthly ₹ per sq.ft.
        "tier_2_city": {"min": 500, "max": 1000, "avg": 700},
        "tier_3_city": {"min": 300, "max": 700, "avg": 500}
    },
    
    "setup_costs_per_sqft": {
        "premium": {"interior": 1500, "fixtures": 800, "signage": 200},
        "standard": {"interior": 1000, "fixtures": 500, "signage": 150},
        "budget": {"interior": 600, "fixtures": 300, "signage": 100}
    },
    
    "inventory_turnover_days": 45,  # Average days to sell inventory
    "gst_rate": 0.18,  # 18% GST
    "itc_lock_in_days": 30  # Days ITC is locked
}

@dataclass
class StoreFinancials:
    """Store financial data structure"""
    store_name: str
    monthly_revenue: float
    monthly_expenses: Dict[str, float]
    gross_margin: float
    inventory_value: float
    investment: float
    start_date: datetime


class ROICalculatorService:
    """Service for ROI calculations and store analysis"""
    
    def __init__(self, db):
        self.db = db
    
    # ==================== PRE-FEASIBILITY ANALYSIS ====================
    
    async def pre_feasibility_analysis(
        self,
        city: str,
        city_tier: str,  # tier_1, tier_2, tier_3
        store_size_sqft: int,
        store_type: str,  # premium, standard, budget
        product_categories: List[str],
        investment_budget: Optional[float] = None,
        target_monthly_revenue: Optional[float] = None,
        use_historical_data: bool = True
    ) -> Dict[str, Any]:
        """
        Generate pre-feasibility analysis for a new store
        """
        try:
            # Get historical data if available
            historical_margins = {}
            if use_historical_data:
                historical_margins = await self._get_historical_margins(product_categories)
            
            # Calculate revenue potential
            revenue_benchmarks = INDUSTRY_BENCHMARKS["revenue_per_sqft"][city_tier]
            
            if target_monthly_revenue:
                estimated_revenue = target_monthly_revenue
            else:
                estimated_revenue = store_size_sqft * revenue_benchmarks["avg"]
            
            min_revenue = store_size_sqft * revenue_benchmarks["min"]
            max_revenue = store_size_sqft * revenue_benchmarks["max"]
            
            # Calculate recommended rent
            rent_ratios = INDUSTRY_BENCHMARKS["rent_to_revenue_ratio"][city_tier]
            recommended_rent = estimated_revenue * rent_ratios["recommended"]
            rent_range = {
                "min": estimated_revenue * rent_ratios["min"],
                "max": estimated_revenue * rent_ratios["max"],
                "recommended": recommended_rent
            }
            
            # Calculate staff requirements & costs
            staff_structure = self._calculate_staff_structure(store_size_sqft, city_tier)
            staff_cost = sum(s["salary"] for s in staff_structure)
            
            # Calculate utilities
            utilities_cost = estimated_revenue * INDUSTRY_BENCHMARKS["utilities_ratio"]
            
            # Calculate marketing budget
            marketing_cost = estimated_revenue * INDUSTRY_BENCHMARKS["marketing_ratio"]
            
            # Calculate setup costs
            setup_costs = INDUSTRY_BENCHMARKS["setup_costs_per_sqft"][store_type]
            interior_cost = store_size_sqft * setup_costs["interior"]
            fixtures_cost = store_size_sqft * setup_costs["fixtures"]
            signage_cost = store_size_sqft * setup_costs["signage"]
            total_setup_cost = interior_cost + fixtures_cost + signage_cost
            
            # Calculate initial inventory
            avg_margin = self._get_blended_margin(product_categories, historical_margins)
            # Inventory = ~45 days of sales at cost
            daily_sales = estimated_revenue / 30
            inventory_at_cost = daily_sales * (1 - avg_margin) * INDUSTRY_BENCHMARKS["inventory_turnover_days"]
            
            # Security deposit (typically 6-12 months rent)
            security_deposit = recommended_rent * 6
            
            # Total investment required
            total_investment = total_setup_cost + inventory_at_cost + security_deposit
            
            # Monthly operating expenses
            monthly_expenses = {
                "rent": recommended_rent,
                "staff_salaries": staff_cost,
                "utilities": utilities_cost,
                "marketing": marketing_cost,
                "miscellaneous": estimated_revenue * INDUSTRY_BENCHMARKS["misc_expenses_ratio"]
            }
            total_monthly_expenses = sum(monthly_expenses.values())
            
            # Breakeven calculation
            gross_profit = estimated_revenue * avg_margin
            net_profit = gross_profit - total_monthly_expenses
            
            if net_profit > 0:
                months_to_breakeven = total_investment / net_profit
            else:
                months_to_breakeven = float('inf')
            
            # GST Working Capital (ITC locked)
            gst_working_capital = inventory_at_cost * INDUSTRY_BENCHMARKS["gst_rate"]
            
            return {
                "status": "success",
                "analysis_type": "pre_feasibility",
                "input_parameters": {
                    "city": city,
                    "city_tier": city_tier,
                    "store_size_sqft": store_size_sqft,
                    "store_type": store_type,
                    "product_categories": product_categories
                },
                "revenue_projections": {
                    "estimated_monthly_revenue": round(estimated_revenue, 0),
                    "min_revenue": round(min_revenue, 0),
                    "max_revenue": round(max_revenue, 0),
                    "revenue_per_sqft": round(estimated_revenue / store_size_sqft, 0)
                },
                "rent_recommendations": {
                    "recommended_rent": round(rent_range["recommended"], 0),
                    "rent_range_min": round(rent_range["min"], 0),
                    "rent_range_max": round(rent_range["max"], 0),
                    "rent_to_revenue_ratio": f"{rent_ratios['recommended']*100:.1f}%"
                },
                "staff_structure": staff_structure,
                "monthly_operating_expenses": {
                    "breakdown": {k: round(v, 0) for k, v in monthly_expenses.items()},
                    "total": round(total_monthly_expenses, 0)
                },
                "setup_investment": {
                    "interior_fit_out": round(interior_cost, 0),
                    "fixtures_furniture": round(fixtures_cost, 0),
                    "signage_branding": round(signage_cost, 0),
                    "initial_inventory": round(inventory_at_cost, 0),
                    "security_deposit": round(security_deposit, 0),
                    "gst_working_capital": round(gst_working_capital, 0),
                    "total_investment": round(total_investment + gst_working_capital, 0)
                },
                "profitability_analysis": {
                    "blended_gross_margin": f"{avg_margin*100:.1f}%",
                    "monthly_gross_profit": round(gross_profit, 0),
                    "monthly_net_profit": round(net_profit, 0),
                    "breakeven_months": round(months_to_breakeven, 1) if months_to_breakeven != float('inf') else "Not Viable",
                    "annual_roi": f"{(net_profit * 12 / total_investment * 100):.1f}%" if net_profit > 0 else "Negative"
                },
                "recommendations": self._generate_prefeasibility_recommendations(
                    net_profit, months_to_breakeven, rent_range, estimated_revenue
                ),
                "data_source": "historical" if historical_margins else "industry_benchmarks",
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Pre-feasibility analysis error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    # ==================== BREAKEVEN CALCULATOR ====================
    
    async def breakeven_analysis(
        self,
        store_name: str,
        monthly_rent: float,
        security_deposit: float,
        interior_setup_cost: float,
        initial_inventory: float,
        staff_salaries: float,
        utilities: float,
        other_expenses: float,
        expected_gross_margin: float,
        target_breakeven_years: int = 2
    ) -> Dict[str, Any]:
        """
        Calculate breakeven for a finalized store with known expenses
        """
        try:
            # Total initial investment
            total_investment = security_deposit + interior_setup_cost + initial_inventory
            
            # Monthly fixed costs
            monthly_fixed_costs = monthly_rent + staff_salaries + utilities + other_expenses
            
            # GST working capital
            gst_working_capital = initial_inventory * INDUSTRY_BENCHMARKS["gst_rate"]
            total_investment += gst_working_capital
            
            # Calculate breakeven revenue
            # Breakeven = Fixed Costs / Gross Margin
            monthly_breakeven_revenue = monthly_fixed_costs / expected_gross_margin
            
            # Calculate revenue needed to recover investment in target years
            target_months = target_breakeven_years * 12
            monthly_profit_needed = total_investment / target_months
            revenue_for_target_breakeven = (monthly_fixed_costs + monthly_profit_needed) / expected_gross_margin
            
            # Year-wise projections
            projections = []
            cumulative_profit = -total_investment  # Start negative (investment)
            
            for year in range(1, 6):  # 5 year projection
                # Assume 10% growth each year after year 1
                growth_factor = 1.0 if year == 1 else (1 + 0.10 * (year - 1))
                annual_revenue = revenue_for_target_breakeven * 12 * growth_factor
                annual_costs = monthly_fixed_costs * 12
                annual_gross_profit = annual_revenue * expected_gross_margin
                annual_net_profit = annual_gross_profit - annual_costs
                cumulative_profit += annual_net_profit
                
                projections.append({
                    "year": year,
                    "revenue": round(annual_revenue, 0),
                    "gross_profit": round(annual_gross_profit, 0),
                    "operating_costs": round(annual_costs, 0),
                    "net_profit": round(annual_net_profit, 0),
                    "cumulative_profit": round(cumulative_profit, 0),
                    "roi_percentage": round((cumulative_profit / total_investment) * 100, 1)
                })
            
            # Sensitivity analysis
            sensitivity = self._sensitivity_analysis(
                monthly_breakeven_revenue, monthly_fixed_costs, 
                expected_gross_margin, total_investment
            )
            
            # Find actual breakeven month
            breakeven_month = None
            cumulative = -total_investment
            monthly_profit = (monthly_breakeven_revenue * expected_gross_margin) - monthly_fixed_costs
            if monthly_profit > 0:
                breakeven_month = int(total_investment / monthly_profit) + 1
            
            return {
                "status": "success",
                "analysis_type": "breakeven",
                "store_name": store_name,
                "investment_summary": {
                    "security_deposit": round(security_deposit, 0),
                    "interior_setup": round(interior_setup_cost, 0),
                    "initial_inventory": round(initial_inventory, 0),
                    "gst_working_capital": round(gst_working_capital, 0),
                    "total_investment": round(total_investment, 0)
                },
                "monthly_costs": {
                    "rent": round(monthly_rent, 0),
                    "staff_salaries": round(staff_salaries, 0),
                    "utilities": round(utilities, 0),
                    "other_expenses": round(other_expenses, 0),
                    "total_fixed_costs": round(monthly_fixed_costs, 0)
                },
                "breakeven_targets": {
                    "monthly_breakeven_revenue": round(monthly_breakeven_revenue, 0),
                    "daily_breakeven_revenue": round(monthly_breakeven_revenue / 30, 0),
                    "revenue_for_target_breakeven": round(revenue_for_target_breakeven, 0),
                    "target_breakeven_years": target_breakeven_years,
                    "estimated_breakeven_month": breakeven_month
                },
                "year_wise_projections": projections,
                "sensitivity_analysis": sensitivity,
                "recommendations": self._generate_breakeven_recommendations(
                    breakeven_month, target_breakeven_years, monthly_profit
                ),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Breakeven analysis error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    # ==================== EXISTING STORE ANALYSIS ====================
    
    async def existing_store_analysis(
        self,
        store_id: str,
        period_months: int = 12
    ) -> Dict[str, Any]:
        """
        Analyze ROI and performance of an existing store using Tally data
        """
        try:
            # Fetch store data
            store = await self.db.stores.find_one({"id": store_id})
            if not store:
                # Try to get from store settings or use default
                store = {"name": f"Store {store_id}", "id": store_id}
            
            # Fetch sales data for the period
            start_date = datetime.now(timezone.utc) - timedelta(days=period_months * 30)
            
            # Get orders/sales
            sales_pipeline = [
                {"$match": {
                    "created_at": {"$gte": start_date.isoformat()},
                    "$or": [
                        {"store_id": store_id},
                        {"source": "tally_import"}
                    ]
                }},
                {"$group": {
                    "_id": None,
                    "total_revenue": {"$sum": "$total_amount"},
                    "total_orders": {"$sum": 1},
                    "total_tax": {"$sum": "$tax_amount"}
                }}
            ]
            
            sales_result = await self.db.orders.aggregate(sales_pipeline).to_list(1)
            sales_data = sales_result[0] if sales_result else {"total_revenue": 0, "total_orders": 0, "total_tax": 0}
            
            # Get purchases/cost of goods
            purchases_pipeline = [
                {"$match": {
                    "created_at": {"$gte": start_date.isoformat()},
                    "$or": [
                        {"store_id": store_id},
                        {"source": "tally_import"}
                    ]
                }},
                {"$group": {
                    "_id": None,
                    "total_purchases": {"$sum": "$total"},
                    "total_purchase_tax": {"$sum": "$tax_total"}
                }}
            ]
            
            purchases_result = await self.db.purchases.aggregate(purchases_pipeline).to_list(1)
            purchases_data = purchases_result[0] if purchases_result else {"total_purchases": 0, "total_purchase_tax": 0}
            
            # Calculate metrics
            total_revenue = sales_data.get("total_revenue", 0)
            total_cogs = purchases_data.get("total_purchases", 0)
            gross_profit = total_revenue - total_cogs
            gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            # ITC Analysis
            output_tax = sales_data.get("total_tax", 0)
            input_tax = purchases_data.get("total_purchase_tax", 0)
            itc_available = input_tax
            net_gst_payable = output_tax - input_tax
            
            # Monthly averages
            monthly_revenue = total_revenue / period_months if period_months > 0 else 0
            monthly_profit = gross_profit / period_months if period_months > 0 else 0
            
            # Get store expenses if available
            expenses = await self._get_store_expenses(store_id, start_date)
            total_expenses = sum(expenses.values())
            net_profit = gross_profit - total_expenses
            
            # Performance vs benchmarks
            performance_rating = self._rate_store_performance(
                gross_margin, monthly_revenue, net_profit
            )
            
            return {
                "status": "success",
                "analysis_type": "existing_store",
                "store_info": {
                    "store_id": store_id,
                    "store_name": store.get("name", f"Store {store_id}"),
                    "analysis_period_months": period_months
                },
                "revenue_analysis": {
                    "total_revenue": round(total_revenue, 0),
                    "total_orders": sales_data.get("total_orders", 0),
                    "average_order_value": round(total_revenue / max(sales_data.get("total_orders", 1), 1), 0),
                    "monthly_average_revenue": round(monthly_revenue, 0)
                },
                "profitability": {
                    "total_cogs": round(total_cogs, 0),
                    "gross_profit": round(gross_profit, 0),
                    "gross_margin_percentage": round(gross_margin, 1),
                    "operating_expenses": round(total_expenses, 0),
                    "net_profit": round(net_profit, 0),
                    "net_margin_percentage": round((net_profit / total_revenue * 100) if total_revenue > 0 else 0, 1)
                },
                "expense_breakdown": {k: round(v, 0) for k, v in expenses.items()},
                "tax_analysis": {
                    "output_gst_collected": round(output_tax, 0),
                    "input_tax_credit_available": round(itc_available, 0),
                    "net_gst_payable": round(net_gst_payable, 0),
                    "itc_utilization_percentage": round((input_tax / output_tax * 100) if output_tax > 0 else 0, 1)
                },
                "performance_rating": performance_rating,
                "recommendations": self._generate_store_recommendations(
                    gross_margin, monthly_revenue, net_profit, expenses
                ),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Existing store analysis error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    # ==================== BUSINESS OVERVIEW (ALL STORES) ====================
    
    async def business_overview(self, period_months: int = 12) -> Dict[str, Any]:
        """
        Get consolidated ROI analysis for all stores
        """
        try:
            # Get all stores
            stores = await self.db.stores.find({}).to_list(100)
            if not stores:
                # Create default stores list
                stores = [{"id": f"store_{i}", "name": f"Store {i}"} for i in range(1, 5)]
            
            store_analyses = []
            total_revenue = 0
            total_profit = 0
            total_investment = 0
            
            for store in stores:
                analysis = await self.existing_store_analysis(store["id"], period_months)
                if analysis["status"] == "success":
                    store_analyses.append(analysis)
                    total_revenue += analysis["revenue_analysis"]["total_revenue"]
                    total_profit += analysis["profitability"]["net_profit"]
            
            # Business level loan/OD as central overhead
            central_overhead = await self._get_central_overhead()
            
            return {
                "status": "success",
                "analysis_type": "business_overview",
                "period_months": period_months,
                "store_count": len(stores),
                "consolidated_financials": {
                    "total_revenue": round(total_revenue, 0),
                    "total_profit_before_overhead": round(total_profit, 0),
                    "central_overhead": round(central_overhead, 0),
                    "net_business_profit": round(total_profit - central_overhead, 0)
                },
                "store_wise_analysis": store_analyses,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Business overview error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    # ==================== HELPER METHODS ====================
    
    async def _get_historical_margins(self, categories: List[str]) -> Dict[str, float]:
        """Get historical margins from Tally data"""
        try:
            margins = {}
            for category in categories:
                # Get average margin from sales vs purchases
                pipeline = [
                    {"$match": {"category": {"$regex": category, "$options": "i"}}},
                    {"$group": {
                        "_id": None,
                        "avg_price": {"$avg": "$price"},
                        "avg_cost": {"$avg": "$purchase_price"}
                    }}
                ]
                result = await self.db.products.aggregate(pipeline).to_list(1)
                if result and result[0].get("avg_price") and result[0].get("avg_cost"):
                    margin = (result[0]["avg_price"] - result[0]["avg_cost"]) / result[0]["avg_price"]
                    margins[category] = margin
            return margins
        except Exception:
            return {}
    
    def _get_blended_margin(self, categories: List[str], historical: Dict[str, float]) -> float:
        """Calculate blended margin across categories"""
        margins = []
        for cat in categories:
            if cat in historical:
                margins.append(historical[cat])
            elif cat in INDUSTRY_BENCHMARKS["gross_margins"]:
                margins.append(INDUSTRY_BENCHMARKS["gross_margins"][cat]["avg"])
            else:
                margins.append(INDUSTRY_BENCHMARKS["gross_margins"]["default"]["avg"])
        return sum(margins) / len(margins) if margins else 0.20
    
    def _calculate_staff_structure(self, sqft: int, city_tier: str) -> List[Dict]:
        """Calculate recommended staff structure"""
        base_salaries = {
            "tier_1_city": {"manager": 45000, "sales": 25000, "helper": 15000},
            "tier_2_city": {"manager": 35000, "sales": 18000, "helper": 12000},
            "tier_3_city": {"manager": 25000, "sales": 15000, "helper": 10000}
        }
        
        salaries = base_salaries.get(city_tier, base_salaries["tier_2_city"])
        
        structure = [{"role": "Store Manager", "count": 1, "salary": salaries["manager"]}]
        
        # 1 sales person per 200 sqft
        sales_count = max(2, sqft // 200)
        structure.append({"role": "Sales Executive", "count": sales_count, "salary": salaries["sales"] * sales_count})
        
        # 1 helper per 400 sqft
        helper_count = max(1, sqft // 400)
        structure.append({"role": "Helper/Delivery", "count": helper_count, "salary": salaries["helper"] * helper_count})
        
        return structure
    
    def _sensitivity_analysis(
        self, 
        base_revenue: float, 
        fixed_costs: float, 
        margin: float,
        investment: float
    ) -> List[Dict]:
        """Generate sensitivity analysis for different scenarios"""
        scenarios = []
        for variance in [-20, -10, 0, 10, 20]:
            adjusted_revenue = base_revenue * (1 + variance/100)
            gross_profit = adjusted_revenue * margin
            net_profit = gross_profit - fixed_costs
            monthly_roi = (net_profit / investment) * 100 if investment > 0 else 0
            
            scenarios.append({
                "scenario": f"{'+' if variance >= 0 else ''}{variance}% Revenue",
                "monthly_revenue": round(adjusted_revenue, 0),
                "monthly_profit": round(net_profit, 0),
                "annual_roi": round(monthly_roi * 12, 1),
                "status": "Profitable" if net_profit > 0 else "Loss"
            })
        return scenarios
    
    async def _get_store_expenses(self, store_id: str, start_date: datetime) -> Dict[str, float]:
        """Get store-wise expenses"""
        # Default expense structure if not tracked separately
        return {
            "rent": 0,
            "salaries": 0,
            "utilities": 0,
            "marketing": 0,
            "maintenance": 0,
            "other": 0
        }
    
    async def _get_central_overhead(self) -> float:
        """Get business-level loan/OD interest as central overhead"""
        # This would be fetched from business settings
        settings = await self.db.business_settings.find_one({"type": "financial"})
        if settings:
            return settings.get("monthly_loan_interest", 0) + settings.get("monthly_od_interest", 0)
        return 0
    
    def _rate_store_performance(self, margin: float, revenue: float, profit: float) -> Dict:
        """Rate store performance against benchmarks"""
        score = 0
        factors = []
        
        if margin >= 20:
            score += 30
            factors.append({"factor": "Gross Margin", "rating": "Excellent", "score": 30})
        elif margin >= 15:
            score += 20
            factors.append({"factor": "Gross Margin", "rating": "Good", "score": 20})
        else:
            score += 10
            factors.append({"factor": "Gross Margin", "rating": "Needs Improvement", "score": 10})
        
        if profit > 0:
            score += 40
            factors.append({"factor": "Profitability", "rating": "Profitable", "score": 40})
        else:
            factors.append({"factor": "Profitability", "rating": "Loss Making", "score": 0})
        
        if revenue > 1000000:  # > 10L monthly
            score += 30
            factors.append({"factor": "Revenue Scale", "rating": "High Volume", "score": 30})
        elif revenue > 500000:
            score += 20
            factors.append({"factor": "Revenue Scale", "rating": "Medium Volume", "score": 20})
        else:
            score += 10
            factors.append({"factor": "Revenue Scale", "rating": "Low Volume", "score": 10})
        
        overall = "Excellent" if score >= 80 else "Good" if score >= 60 else "Average" if score >= 40 else "Needs Attention"
        
        return {
            "overall_score": score,
            "overall_rating": overall,
            "factors": factors
        }
    
    def _generate_prefeasibility_recommendations(
        self, net_profit: float, breakeven_months: float, 
        rent_range: Dict, revenue: float
    ) -> List[str]:
        """Generate recommendations for pre-feasibility"""
        recommendations = []
        
        if net_profit <= 0:
            recommendations.append("⚠️ Current projections show negative profitability. Consider reducing rent or increasing revenue targets.")
        
        if breakeven_months > 36:
            recommendations.append("⚠️ Breakeven period exceeds 3 years. Review investment costs or revenue assumptions.")
        elif breakeven_months > 24:
            recommendations.append("📊 Breakeven in 2-3 years is acceptable but look for cost optimization opportunities.")
        else:
            recommendations.append("✅ Breakeven under 2 years indicates a viable investment.")
        
        recommendations.append(f"💡 Negotiate rent within ₹{rent_range['min']:,.0f} - ₹{rent_range['max']:,.0f} range.")
        recommendations.append("📈 Focus on high-margin categories like Chimneys and Kitchen Sinks to improve profitability.")
        
        return recommendations
    
    def _generate_breakeven_recommendations(
        self, breakeven_month: int, target_years: int, monthly_profit: float
    ) -> List[str]:
        """Generate recommendations for breakeven analysis"""
        recommendations = []
        
        if breakeven_month and breakeven_month <= target_years * 12:
            recommendations.append(f"✅ Target breakeven of {target_years} years is achievable.")
        elif breakeven_month:
            recommendations.append(f"⚠️ Projected breakeven is {breakeven_month} months. Consider cost reduction strategies.")
        else:
            recommendations.append("⚠️ Current projections don't show breakeven. Review pricing and costs.")
        
        if monthly_profit < 50000:
            recommendations.append("💡 Monthly profit margin is thin. Focus on volume growth or margin improvement.")
        
        recommendations.append("📊 Monitor actual vs projected performance monthly.")
        recommendations.append("🎯 Set quarterly revenue targets and review progress.")
        
        return recommendations
    
    def _generate_store_recommendations(
        self, margin: float, revenue: float, profit: float, expenses: Dict
    ) -> List[str]:
        """Generate recommendations for existing store"""
        recommendations = []
        
        if margin < 18:
            recommendations.append("📈 Gross margin below 18%. Review pricing strategy or negotiate better purchase rates.")
        
        if profit < 0:
            recommendations.append("⚠️ Store is currently loss-making. Immediate cost review recommended.")
        
        if expenses.get("rent", 0) > revenue * 0.10:
            recommendations.append("🏠 Rent exceeds 10% of revenue. Consider renegotiation at renewal.")
        
        recommendations.append("✅ Regularly review slow-moving inventory to free up working capital.")
        recommendations.append("📊 Compare performance with other stores to identify best practices.")
        
        return recommendations
