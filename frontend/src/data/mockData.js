// Mock data for Aditya Retail AI Ecommerce Platform

export const mockProducts = [
  // Microwaves & Ovens
  {
    id: 1,
    name: "Hindware Built-In Microwave LORETO 25L",
    category: "Built-In Microven",
    price: 33990,
    originalPrice: 39990,
    images: [
      "https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?ixlib=rb-4.0.3&w=400&h=400&fit=crop",
      "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?ixlib=rb-4.0.3&w=400&h=400&fit=crop",
      "https://images.unsplash.com/photo-1583394838336-acd977736f90?ixlib=rb-4.0.3&w=400&h=400&fit=crop",
      "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?ixlib=rb-4.0.3&w=400&h=400&fit=crop&crop=entropy&cs=tinysrgb"
    ],
    brand: "Hindware",
    description: "Advanced 25L Built-in Microwave with multi-stage cooking, child safety lock, and energy-efficient operation. Perfect for modern Indian kitchens with smart sensor technology.",
    short_description: "25L Built-in Microwave with advanced cooking functions and smart sensors",
    features: [
      "25L Large Capacity", 
      "Built-in Design", 
      "Multi-stage Cooking", 
      "LED Display with Touch Controls",
      "Child Safety Lock",
      "Auto Cook Menus",
      "Energy Efficient Operation"
    ],
    specifications: {
      "Capacity": "25 Liters",
      "Power": "900 Watts",
      "Voltage": "230V, 50Hz",
      "Dimensions": "59.5 x 45.5 x 36.2 cm",
      "Weight": "16 kg",
      "Warranty": "2 Years",
      "Control Type": "Touch Control",
      "Interior Material": "Stainless Steel"
    },
    stock: 15,
    fastMoving: true,
    is_featured: true
  },
  {
    id: 2,
    name: "Hindware Built-In Microwave SPIRO 22L",
    category: "Built-In Microven", 
    price: 29990,
    originalPrice: 32990,
    images: [
      "https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?ixlib=rb-4.0.3&w=400&h=400&fit=crop&crop=faces",
      "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?ixlib=rb-4.0.3&w=400&h=400&fit=crop&crop=center",
      "https://images.unsplash.com/photo-1583394838336-acd977736f90?ixlib=rb-4.0.3&w=400&h=400&fit=crop&crop=top"
    ],
    brand: "Hindware",
    description: "Compact 22L Built-in Microwave with sleek black finish, perfect for small to medium families. Features advanced touch controls and multiple auto-cook programs.",
    short_description: "22L Built-in Microwave with stylish design and smart features",
    features: [
      "22L Compact Capacity", 
      "Sleek Black Design", 
      "Touch Controls", 
      "Child Lock Safety",
      "10 Auto Cook Programs",
      "Defrost Function",
      "Express Cooking"
    ],
    specifications: {
      "Capacity": "22 Liters",
      "Power": "800 Watts", 
      "Voltage": "230V, 50Hz",
      "Dimensions": "55.0 x 42.0 x 34.5 cm",
      "Weight": "14 kg",
      "Warranty": "2 Years",
      "Control Type": "Touch Control",
      "Color": "Black"
    },
    stock: 8,
    fastMoving: false,
    is_featured: false
  },
  {
    id: 3,
    name: "iQ700 Built-in Microwave Oven Black",
    category: "Microwave",
    price: 112690,
    originalPrice: 132490,
    images: [
      "https://adityaretail.com/wp-content/uploads/2024/08/18113214_BE732L1B1_STP_def-1-300x300.webp",
      "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwxfHxtaWNyb3dhdmV8ZW58MHx8fHwxNzU5OTE1MzQzfDA&ixlib=rb-4.1.0&q=85&w=400&h=400&fit=crop",
      "https://images.unsplash.com/photo-1626143508000-4b5904e5e84a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHw0fHxtaWNyb3dhdmV8ZW58MHx8fHwxNzU5OTE1MzQzfDA&ixlib=rb-4.1.0&q=85&w=400&h=400&fit=crop"
    ],
    brand: "Siemens",
    description: "Premium built-in microwave with advanced features",
    features: ["Premium Quality", "Smart Sensors", "Auto Programs", "Black Finish"],
    stock: 5,
    fastMoving: true
  },
  // Cooking Ranges
  {
    id: 4,
    name: "Dona FB 4B 60 Cooking Range",
    category: "Cooking Range",
    price: 59990,
    originalPrice: null,
    images: [
      "https://adityaretail.com/wp-content/uploads/2024/08/DONA-4B-60-picture-1-300x300.webp",
      "https://images.unsplash.com/photo-1629234356883-c37e616a2d43?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHxjb29rdG9wfGVufDB8fHx8MTc1OTkxNTM1NHww&ixlib=rb-4.1.0&q=85&w=400&h=400&fit=crop",
      "https://images.unsplash.com/photo-1722942722302-3e8a6dd7e77c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHwzfHxraXRjaGVuJTIwYXBwbGlhbmNlc3xlbnwwfHx8fDE3NTk5MTUzMzd8MA&ixlib=rb-4.1.0&q=85&w=400&h=400&fit=crop"
    ],
    brand: "Dona",
    description: "4 Burner cooking range with oven",
    features: ["4 Burners", "Built-in Oven", "Auto Ignition", "Safety Features"],
    stock: 12,
    fastMoving: true
  },
  // Induction Cooktops
  {
    id: 5,
    name: "Dino Induction Cooktop",
    category: "Induction",
    price: 4490,
    originalPrice: null,
    images: [
      "https://adityaretail.com/wp-content/uploads/2024/08/dino-induction-min-300x300.webp",
      "https://images.unsplash.com/photo-1629234356883-c37e616a2d43?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHxjb29rdG9wfGVufDB8fHx8MTc1OTkxNTM1NHww&ixlib=rb-4.1.0&q=85&w=400&h=400&fit=crop"
    ],
    brand: "Dino",
    description: "Efficient induction cooktop for modern kitchens",
    features: ["2000W Power", "Touch Controls", "Energy Efficient", "Compact Design"],
    stock: 25,
    fastMoving: true
  },
  {
    id: 6,
    name: "iQ700 Flex Induction Cooktop 30 Cm Black",
    category: "Induction",
    price: 109640,
    originalPrice: 128990,
    images: [
      "https://adityaretail.com/wp-content/uploads/2024/08/MCSA02951092_EX375FXB5I_ElectricHob_Siemens_STP_def-300x300.webp",
      "https://images.unsplash.com/photo-1629234356883-c37e616a2d43?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHxjb29rdG9wfGVufDB8fHx8MTc1OTkxNTM1NHww&ixlib=rb-4.1.0&q=85&w=400&h=400&fit=crop"
    ],
    brand: "Siemens",
    description: "Premium flex induction with advanced technology",
    features: ["FlexInduction Zone", "Touch Control", "30cm Width", "Premium Black"],
    stock: 3,
    fastMoving: false
  },
  // Washing Machines
  {
    id: 7,
    name: "Series 6 Washing Machine Top Loader 680 RPM",
    category: "10 KG TOP LOAD WM",
    price: 48390,
    originalPrice: null,
    images: [
      "https://adityaretail.com/wp-content/uploads/2024/07/19574348_WOI105B0IN_STP_def.webp",
      "https://images.unsplash.com/photo-1626806819282-2c1dc01a5e0c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwxfHx3YXNoaW5nJTIwbWFjaGluZXxlbnwwfHx8fDE3NTk5MTUzODV8MA&ixlib=rb-4.1.0&q=85&w=400&h=400&fit=crop",
      "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwyfHx3YXNoaW5nJTIwbWFjaGluZXxlbnwwfHx8fDE3NTk5MTUzODV8MA&ixlib=rb-4.1.0&q=85&w=400&h=400&fit=crop"
    ],
    brand: "Bosch",
    description: "10kg top loading washing machine with multiple programs",
    features: ["10kg Capacity", "680 RPM", "Multiple Programs", "Digital Display"],
    stock: 7,
    fastMoving: true
  },
  // Fridges
  {
    id: 8,
    name: "Series 4 Free-standing Fridge 147.4 X 53.8 Cm Mid Night Blue",
    category: "226 Liters Single Door Fridge",
    price: 30490,
    originalPrice: null,
    images: [
      "https://adityaretail.com/wp-content/uploads/2024/07/23139045_CST22U14PI_STP_def-300x300.webp",
      "https://images.unsplash.com/photo-1484154218962-a197022b5858?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHw0fHxraXRjaGVuJTIwYXBwbGlhbmNlc3xlbnwwfHx8fDE3NTk5MTUzMzd8MA&ixlib=rb-4.1.0&q=85&w=400&h=400&fit=crop"
    ],
    brand: "Bosch",
    description: "226L single door refrigerator in midnight blue",
    features: ["226L Capacity", "Single Door", "Energy Efficient", "Midnight Blue"],
    stock: 10,
    fastMoving: true
  },
  // Chimneys/Hoods
  {
    id: 9,
    name: "Series 4 Wall-mounted Cooker Hood 90 Cm Flat Black",
    category: "Hood",
    price: 58990,
    originalPrice: null,
    images: [
      "https://adityaretail.com/wp-content/uploads/2024/07/21089725_DWKA98H60I_STP_def-300x300.webp",
      "https://images.unsplash.com/photo-1556908493-4ac5f138ab77?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwxfHxraXRjaGVuJTIwaG9vZHxlbnwwfHx8fDE3NTk5MTUzOTB8MA&ixlib=rb-4.1.0&q=85&w=400&h=400&fit=crop"
    ],
    brand: "Bosch",
    description: "90cm wall mounted cooker hood with LED controls",
    features: ["90cm Width", "LED Controls", "Air Extraction", "Touch Control"],
    stock: 6,
    fastMoving: false
  }
];

export const categories = [
  {
    id: 1,
    name: "Washing Machine",
    subcategories: ["Front Load", "Top Load", "Washer Dryer", "10 KG TOP LOAD WM", "7KG WASHING MACHINE"]
  },
  {
    id: 2,
    name: "Refrigerator",
    subcategories: ["Built-In Fridge", "Built-In Freezer", "Freestanding", "noFrost", "hyperFresh", "Home Connect"]
  },
  {
    id: 3,
    name: "Gas Hob",
    subcategories: ["60cm", "75cm", "90cm", "Domino 30cm", "Wok Burner", "stepFlame Technology"]
  },
  {
    id: 4,
    name: "Induction Hob",
    subcategories: ["60cm", "80cm", "Domino 30cm", "InductionAir", "flexInduction", "powerMove Plus"]
  },
  {
    id: 5,
    name: "Dishwasher",
    subcategories: ["Free-Standing", "Fully Integrated", "Semi-Integrated", "12-14 Place Settings", "Home Connect", "Zeolith Drying"]
  },
  {
    id: 6,
    name: "Sink",
    subcategories: ["Designer Sinks", "Granite Sinks", "Handmade Sinks", "Undermount Sinks"]
  },
  {
    id: 7,
    name: "Chimney",
    subcategories: ["Autoclean", "BLDC", "Decorative", "IoT Chimney", "Island Chimney"]
  },
  {
    id: 8,
    name: "Oven",
    subcategories: ["Built-in Oven", "Built-in Microven", "Combi Oven", "Microwave", "Warming Drawer"]
  },
  {
    id: 9,
    name: "Mixer Grinder",
    subcategories: ["500W", "600W", "750W", "1000W", "TrueMixx Series", "Stone Pounding"]
  },
  {
    id: 10,
    name: "Air Fryer",
    subcategories: ["Series 2", "Series 6", "6L Capacity", "8L Capacity", "Digital Display", "11 Auto Programs"]
  },
  {
    id: 11,
    name: "Coffee Machine",
    subcategories: ["Built-In", "Fully Automatic", "Series 2", "Series 6", "Series 8", "Home Connect"]
  },
  {
    id: 12,
    name: "Detergent",
    subcategories: ["Dishwasher Detergent", "Washing Machine Detergent", "Fabric Softener"]
  }
];

export const trustBadges = [
  {
    icon: "Truck",
    title: "Free Delivery",
    subtitle: "Across India"
  },
  {
    icon: "ThumbsUp", 
    title: "99% Positive",
    subtitle: "Feedbacks"
  },
  {
    icon: "RotateCcw",
    title: "2 days",
    subtitle: "for free return"
  },
  {
    icon: "Shield",
    title: "Payment",
    subtitle: "Secure System"
  },
  {
    icon: "Award",
    title: "Only Best",
    subtitle: "Brands"
  }
];

export const heroBanners = [
  {
    id: 1,
    title: "Catch Hottest DEALS in Kitchen Appliances",
    subtitle: "Shop now",
    image: "https://adityaretail.com/wp-content/uploads/2025/03/Mixer.jpg",
    link: "/category/kitchen-appliances"
  },
  {
    id: 2,
    title: "Clean Clothes, Fresh Smells AND MORE",
    subtitle: "Shop now", 
    image: "https://adityaretail.com/wp-content/uploads/2025/03/Washing-Machine.jpg",
    link: "/category/washing-machine"
  },
  {
    id: 3,
    title: "Chimneys, Cooktops AND MORE",
    subtitle: "Shop now",
    image: "https://adityaretail.com/wp-content/uploads/2025/03/chimney.jpg", 
    link: "/category/chimney"
  },
  {
    id: 4,
    title: "The new SMART OVENS for effortless cooking",
    subtitle: "Shop now",
    image: "https://adityaretail.com/wp-content/uploads/2025/03/Oven.jpg",
    link: "/category/oven"
  }
];

export const brands = ["Bosch", "Siemens", "Hindware"];

// AI Agent Mock Responses
export const aiAgentResponses = {
  sales: {
    greeting: "Hello! I'm your personal sales assistant. I can help you find the perfect appliance, provide detailed product information, and even negotiate the best price for you. What are you looking for today?",
    productRecommendation: "Based on your needs, I'd recommend the Hindware Built-In Microwave LORETO 25L. It's perfect for a family of 4-5 people and currently we have a special offer - I can give you 5% discount making it ₹32,290. Would you like to know more about its features?",
    priceNegotiation: "I understand budget is important. Let me check what I can do for you... I can offer you a special price of ₹31,500 for the LORETO 25L, plus free installation worth ₹2,000. This is the best price I can offer. Shall we proceed?"
  },
  service: {
    greeting: "Hi! I'm your service support agent. I can help you with installation, troubleshooting, warranty claims, and service requests. How can I assist you today?",
    troubleshooting: "I see you're having an issue with your microwave not heating properly. Here are some quick troubleshooting steps:\n1. Check if the door is closing properly\n2. Ensure the turntable is in place\n3. Try cleaning the magnetron vents\n\nIf these don't help, I'll create a service request for you.",
    serviceRequest: "I've created a service request #SR2024001 for your microwave heating issue. Our certified technician will contact you within 24 hours to schedule a visit. You'll receive an email confirmation shortly."
  },
  stock: {
    greeting: "I'm your inventory management assistant. I can provide real-time stock updates, reorder alerts, and inventory analysis.",
    stockAlert: "⚠️ Low Stock Alert: Dino Induction Cooktop - Only 3 units left. This is a fast-moving item. Recommend reordering 20 units to maintain optimal inventory levels.",
    inventoryReport: "Current Inventory Status:\n• Fast Moving: 5 items need immediate reorder\n• Slow Moving: 3 items showing excess stock\n• Total Value: ₹15,67,890\n• Turnover Rate: 85% (Excellent)"
  },
  marketing: {
    greeting: "Hello! I'm your marketing assistant. I create campaigns, analyze customer behavior, and drive sales through targeted promotions.",
    campaign: "🎯 New Campaign Suggestion: 'Festive Kitchen Upgrade' - Bundle offers on microwave + induction combos with 15% discount. Expected to increase average order value by 25%.",
    remarketing: "I've identified 150 customers who viewed microwaves but didn't purchase. Launching personalized email campaign with 10% discount code valid for 48 hours."
  },
  delivery: {
    greeting: "Hi! I'm your delivery coordination agent. I handle order fulfillment, tracking, and customer delivery updates.",
    orderUpdate: "📦 Order #AD2024001: Your Hindware Microwave LORETO 25L is packed and ready for dispatch. Estimated delivery: Tomorrow by 6 PM. Track: bit.ly/track-AD2024001",
    deliverySchedule: "Delivery scheduled for tomorrow 2-6 PM. Our partner will call you 30 minutes before arrival. For any delivery concerns, I'm here to help 24/7."
  }
};