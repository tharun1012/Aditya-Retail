"""
Role and Permission Management System
Defines available roles, modules, and their permissions
"""

# Available permission modules - matching dashboard modules
PERMISSION_MODULES = {
    # Operations
    "products": {
        "name": "Product Manager",
        "category": "operations",
        "permissions": ["view", "create", "edit", "delete"]
    },
    "orders": {
        "name": "Orders & Sales",
        "category": "operations",
        "permissions": ["view", "create", "edit", "delete", "refund"]
    },
    "inventory": {
        "name": "Inventory & Stock",
        "category": "operations",
        "permissions": ["view", "create", "edit", "delete", "transfer"]
    },
    "delivery": {
        "name": "Delivery Management",
        "category": "operations",
        "permissions": ["view", "edit", "assign", "track"]
    },
    "service_tickets": {
        "name": "Service Tickets",
        "category": "operations",
        "permissions": ["view", "create", "edit", "delete", "resolve"]
    },
    
    # Accounting & Finance
    "accounting": {
        "name": "Accounting Dashboard",
        "category": "accounting",
        "permissions": ["view", "edit"]
    },
    "tally_import": {
        "name": "Tally Data Import",
        "category": "accounting",
        "permissions": ["view", "import", "delete"]
    },
    "purchase_orders": {
        "name": "Purchase Orders",
        "category": "accounting",
        "permissions": ["view", "create", "edit", "delete", "approve"]
    },
    "purchase_bills": {
        "name": "Purchase Bills",
        "category": "accounting",
        "permissions": ["view", "create", "edit", "delete", "pay"]
    },
    "goods_receipt": {
        "name": "Goods Receipt",
        "category": "accounting",
        "permissions": ["view", "create", "edit", "delete"]
    },
    "gst_reports": {
        "name": "GST Reports",
        "category": "accounting",
        "permissions": ["view", "export", "file"]
    },
    "compliance": {
        "name": "Compliance & Audits",
        "category": "accounting",
        "permissions": ["view", "edit", "lock", "unlock"]
    },
    "quotations": {
        "name": "Quotations",
        "category": "accounting",
        "permissions": ["view", "create", "edit", "delete", "convert"]
    },
    "reports_exports": {
        "name": "Reports & Exports",
        "category": "accounting",
        "permissions": ["view", "export"]
    },
    "ai_ca_assistant": {
        "name": "AI CA Assistant",
        "category": "accounting",
        "permissions": ["view", "chat"]
    },
    "daily_accounting_reports": {
        "name": "Daily Accounting Reports",
        "category": "accounting",
        "permissions": ["view", "export"]
    },
    "offline_invoices": {
        "name": "Offline Invoices",
        "category": "accounting",
        "permissions": ["view", "create", "edit", "delete"]
    },
    "sales_order_conversion": {
        "name": "Sales Order Conversion",
        "category": "accounting",
        "permissions": ["view", "convert"]
    },
    "sales_invoices": {
        "name": "Sales Invoices",
        "category": "accounting",
        "permissions": ["view", "create", "edit", "delete"]
    },
    "hsn_management": {
        "name": "HSN Code Management",
        "category": "accounting",
        "permissions": ["view", "create", "edit", "delete"]
    },
    "po_requests": {
        "name": "PO Requests",
        "category": "accounting",
        "permissions": ["view", "approve", "reject"]
    },
    "stock_reconciliation": {
        "name": "Stock Reconciliation",
        "category": "accounting",
        "permissions": ["view", "edit"]
    },
    "stock_transfer_approval": {
        "name": "Stock Transfer Approval",
        "category": "accounting",
        "permissions": ["view", "approve", "reject"]
    },
    "draft_products_review": {
        "name": "Draft Products Review",
        "category": "accounting",
        "permissions": ["view", "edit", "publish"]
    },
    "incomplete_products": {
        "name": "Incomplete Products",
        "category": "accounting",
        "permissions": ["view", "edit"]
    },
    "party_ledger": {
        "name": "Party Ledger",
        "category": "accounting",
        "permissions": ["view", "edit"]
    },
    "journal_vouchers": {
        "name": "Journal Vouchers",
        "category": "accounting",
        "permissions": ["view", "create", "edit", "delete"]
    },
    "bank_reconciliation": {
        "name": "Bank Reconciliation",
        "category": "accounting",
        "permissions": ["view", "edit"]
    },
    "landed_cost_calculator": {
        "name": "Landed Cost Calculator",
        "category": "accounting",
        "permissions": ["view", "calculate"]
    },
    "payment_reminders": {
        "name": "Payment Reminders",
        "category": "accounting",
        "permissions": ["view", "send"]
    },
    "financial_reports": {
        "name": "Financial Reports",
        "category": "accounting",
        "permissions": ["view", "export"]
    },
    "expense_management": {
        "name": "Expense Management",
        "category": "accounting",
        "permissions": ["view", "create", "edit", "delete"]
    },
    "vouchers_notes": {
        "name": "Vouchers & Notes",
        "category": "accounting",
        "permissions": ["view", "create", "edit", "delete"]
    },
    "delivery_challans": {
        "name": "Delivery Challans",
        "category": "accounting",
        "permissions": ["view", "create", "edit", "delete"]
    },
    "delivery_personnel": {
        "name": "Delivery Personnel",
        "category": "accounting",
        "permissions": ["view", "create", "edit", "delete"]
    },
    "pine_labs_transactions": {
        "name": "Pine Labs Transactions",
        "category": "accounting",
        "permissions": ["view", "reconcile"]
    },
    "store_document_manager": {
        "name": "Store Document Manager",
        "category": "accounting",
        "permissions": ["view", "edit"]
    },
    
    # Customer Management
    "customers": {
        "name": "Customer CRM",
        "category": "customers",
        "permissions": ["view", "create", "edit", "delete"]
    },
    "leads": {
        "name": "Lead Management",
        "category": "customers",
        "permissions": ["view", "create", "edit", "delete", "assign", "convert"]
    },
    "consultations": {
        "name": "Expert Consultations",
        "category": "customers",
        "permissions": ["view", "schedule", "complete"]
    },
    "customer_journey": {
        "name": "Customer Journey",
        "category": "customers",
        "permissions": ["view", "export"]
    },
    
    # Marketing
    "combo_offers": {
        "name": "Combo & Bundle Offers",
        "category": "marketing",
        "permissions": ["view", "create", "edit", "delete", "publish"]
    },
    "cashback_offers": {
        "name": "Cashback & Bank Offers",
        "category": "marketing",
        "permissions": ["view", "create", "edit", "delete"]
    },
    "promotions": {
        "name": "Promotions & Themes",
        "category": "marketing",
        "permissions": ["view", "create", "edit", "delete", "publish"]
    },
    "banners": {
        "name": "Banner Management",
        "category": "marketing",
        "permissions": ["view", "create", "edit", "delete", "publish"]
    },
    "campaigns": {
        "name": "Marketing Campaigns",
        "category": "marketing",
        "permissions": ["view", "create", "edit", "delete", "launch"]
    },
    "social_media": {
        "name": "Social Media Posts",
        "category": "marketing",
        "permissions": ["view", "create", "edit", "delete", "publish"]
    },
    "blog": {
        "name": "Blog",
        "category": "marketing",
        "permissions": ["view", "create", "edit", "delete", "publish"]
    },
    "new_product_highlighting": {
        "name": "New Product Highlighting",
        "category": "marketing",
        "permissions": ["view", "edit"]
    },
    
    # Analytics
    "analytics": {
        "name": "Analytics Dashboard",
        "category": "analytics",
        "permissions": ["view", "export"]
    },
    "ai_agents": {
        "name": "AI Agents Performance",
        "category": "analytics",
        "permissions": ["view", "configure"]
    },
    "marketing_analytics": {
        "name": "Marketing Analytics",
        "category": "analytics",
        "permissions": ["view", "export"]
    },
    "ai_marketing_agent": {
        "name": "AI Marketing Agent",
        "category": "analytics",
        "permissions": ["view", "configure"]
    },
    "website_analytics": {
        "name": "Website Analytics",
        "category": "analytics",
        "permissions": ["view", "export"]
    },
    "roi_calculator": {
        "name": "ROI Calculator",
        "category": "analytics",
        "permissions": ["view"]
    },
    "lead_scraping": {
        "name": "Lead Scraping",
        "category": "analytics",
        "permissions": ["view", "configure"]
    },
    
    # Configuration
    "categories": {
        "name": "Category Management",
        "category": "config",
        "permissions": ["view", "create", "edit", "delete"]
    },
    "knowledge_base": {
        "name": "Knowledge Base",
        "category": "config",
        "permissions": ["view", "create", "edit", "delete"]
    },
    "document_numbering": {
        "name": "Document Numbering",
        "category": "config",
        "permissions": ["view", "edit"]
    },
    "seo_manager": {
        "name": "SEO Manager",
        "category": "config",
        "permissions": ["view", "edit"]
    },
    "image_manager": {
        "name": "Image Manager",
        "category": "config",
        "permissions": ["view", "edit"]
    },
    "data_management": {
        "name": "Data Management",
        "category": "config",
        "permissions": ["view", "edit", "delete", "backup"]
    },
    "fy_transition_tools": {
        "name": "FY Transition Tools",
        "category": "config",
        "permissions": ["view", "edit"]
    },
    
    # Admin Only
    "stores": {
        "name": "Store Management",
        "category": "admin",
        "permissions": ["view", "create", "edit", "delete", "permissions"]
    },
    "team": {
        "name": "Team/User Management",
        "category": "admin",
        "permissions": ["view", "create", "edit", "delete", "permissions"]
    },
    "system_settings": {
        "name": "System Settings",
        "category": "admin",
        "permissions": ["view", "edit"]
    },
    "admin_settings": {
        "name": "Admin Settings",
        "category": "admin",
        "permissions": ["view", "edit"]
    },
    "admin_user_management": {
        "name": "Admin User Management",
        "category": "admin",
        "permissions": ["view", "create", "edit", "delete"]
    }
}

# Pre-defined role templates
ROLE_TEMPLATES = {
    # Admin Level Roles
    "super_admin": {
        "name": "Super Admin",
        "level": "admin",
        "description": "Full system access with all permissions including user management",
        "permissions": {module: perms["permissions"] for module, perms in PERMISSION_MODULES.items()}
    },
    "accounts_admin": {
        "name": "Accounts Admin",
        "level": "admin",
        "description": "Full access to all accounting and finance modules",
        "permissions": {
            "accounting": ["view", "edit"],
            "tally_import": ["view", "import", "delete"],
            "purchase_orders": ["view", "create", "edit", "delete", "approve"],
            "purchase_bills": ["view", "create", "edit", "delete", "pay"],
            "goods_receipt": ["view", "create", "edit", "delete"],
            "gst_reports": ["view", "export", "file"],
            "compliance": ["view", "edit", "lock", "unlock"],
            "quotations": ["view", "create", "edit", "delete", "convert"],
            "reports_exports": ["view", "export"],
            "orders": ["view"],
            "customers": ["view"],
            "analytics": ["view", "export"]
        }
    },
    "marketing_admin": {
        "name": "Marketing Admin",
        "level": "admin",
        "description": "Full access to all marketing and campaign modules",
        "permissions": {
            "combo_offers": ["view", "create", "edit", "delete", "publish"],
            "promotions": ["view", "create", "edit", "delete", "publish"],
            "banners": ["view", "create", "edit", "delete", "publish"],
            "campaigns": ["view", "create", "edit", "delete", "launch"],
            "social_media": ["view", "create", "edit", "delete", "publish"],
            "blog": ["view", "create", "edit", "delete", "publish"],
            "marketing_analytics": ["view", "export"],
            "products": ["view"],
            "customers": ["view"],
            "leads": ["view", "create", "edit"],
            "analytics": ["view"]
        }
    },
    "operations_admin": {
        "name": "Operations Admin",
        "level": "admin",
        "description": "Full access to all operational modules",
        "permissions": {
            "products": ["view", "create", "edit", "delete"],
            "orders": ["view", "create", "edit", "delete", "refund"],
            "inventory": ["view", "create", "edit", "delete", "transfer"],
            "delivery": ["view", "edit", "assign", "track"],
            "service_tickets": ["view", "create", "edit", "delete", "resolve"],
            "customers": ["view", "create", "edit"],
            "analytics": ["view", "export"]
        }
    },
    
    # Manager Level Roles
    "general_manager": {
        "name": "General Manager",
        "level": "manager",
        "description": "Store/department manager with broad operational access",
        "permissions": {
            "products": ["view", "edit"],
            "orders": ["view", "edit"],
            "inventory": ["view", "edit"],
            "delivery": ["view", "assign"],
            "service_tickets": ["view", "edit", "resolve"],
            "customers": ["view", "edit"],
            "leads": ["view", "edit", "assign"],
            "quotations": ["view", "create", "edit"],
            "analytics": ["view"],
            "ai_agents": ["view"]
        }
    },
    "accounts_manager": {
        "name": "Accounts Manager",
        "level": "manager",
        "description": "Manages accounting operations without admin privileges",
        "permissions": {
            "accounting": ["view", "edit"],
            "tally_import": ["view", "import"],
            "purchase_orders": ["view", "create", "edit"],
            "purchase_bills": ["view", "create", "edit"],
            "goods_receipt": ["view", "create", "edit"],
            "gst_reports": ["view", "export"],
            "quotations": ["view", "create", "edit"],
            "reports_exports": ["view", "export"],
            "orders": ["view"],
            "customers": ["view"]
        }
    },
    "marketing_manager": {
        "name": "Marketing Manager",
        "level": "manager",
        "description": "Manages marketing campaigns and promotions",
        "permissions": {
            "combo_offers": ["view", "create", "edit"],
            "promotions": ["view", "create", "edit"],
            "banners": ["view", "create", "edit"],
            "campaigns": ["view", "create", "edit"],
            "social_media": ["view", "create", "edit"],
            "blog": ["view", "create", "edit", "publish"],
            "marketing_analytics": ["view"],
            "products": ["view"],
            "leads": ["view"]
        }
    },
    
    # Staff Level Roles
    "sales_staff": {
        "name": "Sales Staff",
        "level": "staff",
        "description": "Sales team member with lead and order management",
        "permissions": {
            "products": ["view"],
            "orders": ["view", "create", "edit"],
            "leads": ["view", "create", "edit"],
            "customers": ["view", "create", "edit"],
            "quotations": ["view", "create"],
            "inventory": ["view"]
        }
    },
    "accounts_staff": {
        "name": "Accounts Staff",
        "level": "staff",
        "description": "Handles day-to-day accounting entries",
        "permissions": {
            "accounting": ["view"],
            "purchase_orders": ["view", "create"],
            "purchase_bills": ["view", "create"],
            "goods_receipt": ["view", "create"],
            "gst_reports": ["view"],
            "quotations": ["view", "create"],
            "orders": ["view"],
            "customers": ["view"]
        }
    },
    "service_staff": {
        "name": "Service Staff",
        "level": "staff",
        "description": "Service team member handling tickets and support",
        "permissions": {
            "products": ["view"],
            "service_tickets": ["view", "create", "edit", "resolve"],
            "customers": ["view", "edit"],
            "inventory": ["view"]
        }
    },
    "marketing_staff": {
        "name": "Marketing Staff",
        "level": "staff",
        "description": "Marketing team member for content creation",
        "permissions": {
            "combo_offers": ["view", "create"],
            "promotions": ["view", "create"],
            "banners": ["view", "create"],
            "campaigns": ["view", "create"],
            "social_media": ["view", "create", "edit"],
            "blog": ["view", "create", "edit"],
            "products": ["view"]
        }
    },
    "delivery_staff": {
        "name": "Delivery Staff",
        "level": "staff",
        "description": "Delivery team member for order fulfillment",
        "permissions": {
            "orders": ["view", "edit"],
            "delivery": ["view", "edit"],
            "customers": ["view"]
        }
    },
    "warehouse_staff": {
        "name": "Warehouse Staff",
        "level": "staff",
        "description": "Warehouse team member for inventory management",
        "permissions": {
            "products": ["view"],
            "inventory": ["view", "edit"],
            "delivery": ["view"]
        }
    },
    "data_analyst": {
        "name": "Data Analyst",
        "level": "staff",
        "description": "Analyst with read-only access to reports and analytics",
        "permissions": {
            "products": ["view"],
            "orders": ["view"],
            "customers": ["view"],
            "leads": ["view"],
            "analytics": ["view", "export"],
            "marketing_analytics": ["view", "export"],
            "gst_reports": ["view", "export"],
            "reports_exports": ["view", "export"]
        }
    }
}


def check_permission(user_permissions: dict, module: str, action: str) -> bool:
    """
    Check if user has permission for a specific action on a module
    
    Args:
        user_permissions: User's permission dictionary
        module: Module name (e.g., 'products', 'orders')
        action: Action name (e.g., 'view', 'create', 'edit', 'delete')
    
    Returns:
        bool: True if user has permission, False otherwise
    """
    if not user_permissions:
        return False
    
    module_perms = user_permissions.get(module, [])
    return action in module_perms


def get_user_accessible_modules(user_permissions: dict) -> list:
    """
    Get list of modules user can access (has at least view permission)
    
    Args:
        user_permissions: User's permission dictionary
    
    Returns:
        list: List of accessible module names
    """
    accessible = []
    for module, perms in user_permissions.items():
        if "view" in perms:
            accessible.append(module)
    return accessible


def get_modules_by_category() -> dict:
    """
    Get modules grouped by category
    
    Returns:
        dict: Modules grouped by category
    """
    categories = {}
    for module_id, module_info in PERMISSION_MODULES.items():
        category = module_info.get("category", "other")
        if category not in categories:
            categories[category] = []
        categories[category].append({
            "id": module_id,
            "name": module_info["name"],
            "permissions": module_info["permissions"]
        })
    return categories


def get_roles_by_level() -> dict:
    """
    Get roles grouped by level (admin, manager, staff)
    
    Returns:
        dict: Roles grouped by level
    """
    levels = {"admin": [], "manager": [], "staff": []}
    for role_id, role_info in ROLE_TEMPLATES.items():
        level = role_info.get("level", "staff")
        if level in levels:
            levels[level].append({
                "id": role_id,
                "name": role_info["name"],
                "description": role_info["description"]
            })
    return levels
