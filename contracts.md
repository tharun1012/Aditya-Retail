# Aditya Retail AI Ecommerce Platform - Integration Contracts

## API Contracts

### Base URL
- Development: `http://localhost:8001/api`
- Production: Uses `REACT_APP_BACKEND_URL` from environment

### Core Endpoints

#### Products
- `GET /api/products` - Get all products with filtering
  - Query params: `category`, `brand`, `min_price`, `max_price`, `in_stock`
- `GET /api/products/{id}` - Get single product
- `POST /api/products` - Create new product (admin)

#### Cart Management  
- `POST /api/cart/add` - Add item to cart
  - Body: `{product_id, quantity, session_id?}`
- `GET /api/cart/{session_id}` - Get cart contents with product details

#### Orders
- `POST /api/orders` - Create new order
- `GET /api/orders/{order_id}` - Get order details

#### AI Agents
- `POST /api/ai/chat` - Chat with AI agents
  - Body: `{session_id, agent_type, message, context?}`
  - Agent types: `sales`, `service`, `stock`, `marketing`, `delivery`
- `GET /api/ai/chat/history/{session_id}` - Get chat history
- `POST /api/ai/service/request` - Create service request
- `GET /api/ai/inventory/analysis` - Get inventory analysis
- `GET /api/ai/marketing/insights` - Get marketing insights
- `POST /api/ai/delivery/update` - Update delivery status

## Data Migration from Mock to Backend

### Products Data
- **Mock Location**: `/frontend/src/data/mockData.js` - `mockProducts` array
- **Backend Model**: `/backend/models.py` - `Product` class
- **Integration**: Products automatically seeded on backend startup
- **Frontend Update**: Replace mock data calls with API calls to `/api/products`

### Categories and Brands
- **Mock Location**: `mockData.js` - `categories` array  
- **Backend Endpoints**: `/api/categories`, `/api/brands`
- **Integration**: Dynamic loading from database

### Cart Functionality
- **Mock Location**: Frontend localStorage management in `App.js`
- **Backend Model**: `Cart` and `CartItem` models with session-based storage
- **Integration**: Replace localStorage with API calls using session ID

### AI Chat Integration
- **Mock Location**: `aiAgentResponses` object in `mockData.js`
- **Backend Integration**: Real AI agents using OpenAI GPT-4 via Emergent LLM key
- **Features**: 
  - Persistent chat history in MongoDB
  - Context-aware responses based on products and user behavior
  - Real business logic for inventory, service requests, etc.

## Frontend Integration Tasks

### 1. API Service Layer (Priority: High)
- Create `/frontend/src/services/api.js` with axios configuration
- Implement error handling and loading states
- Add request/response interceptors for session management

### 2. Replace Mock Data (Priority: High)
- Update `ProductGrid` component to use API endpoint
- Replace hardcoded categories with dynamic loading  
- Implement real-time stock updates

### 3. AI Chat Enhancement (Priority: Medium)
- Connect `AIChat` component to `/api/ai/chat` endpoint
- Implement persistent chat history
- Add typing indicators and better UX

### 4. Cart Integration (Priority: Medium)  
- Replace localStorage cart with API-based cart
- Implement session-based cart persistence
- Add cart synchronization across tabs

### 5. Service Request Flow (Priority: Low)
- Create service request forms
- Integrate with AI Service Agent for ticket creation
- Add email notifications (future enhancement)

## Backend Features Implemented

### AI Agents
✅ **Sales Agent**: Product recommendations, pricing negotiation, upselling
✅ **Service Agent**: Troubleshooting, service request creation, warranty support  
✅ **Stock Manager**: Inventory analysis, reorder alerts, stock optimization
✅ **Marketing Agent**: Campaign suggestions, customer behavior analysis
✅ **Delivery Agent**: Order tracking, delivery updates, logistics coordination

### Business Logic
✅ **Inventory Management**: Real-time stock tracking, low stock alerts
✅ **Order Processing**: Complete order lifecycle management  
✅ **Analytics**: Product performance, customer behavior tracking
✅ **Service Requests**: Ticket creation and management system

### Database Schema
✅ **Products**: Complete product catalog with inventory
✅ **Orders**: Order management with item details
✅ **Cart**: Session-based shopping cart
✅ **Chat**: AI conversation history and sessions
✅ **Service Requests**: Customer support ticket system
✅ **Analytics**: Inventory alerts and marketing insights

## Implementation Priority

1. **Phase 1**: API service layer and product loading (30 min)
2. **Phase 2**: AI chat integration with real backend (45 min)
3. **Phase 3**: Cart and order management (30 min)  
4. **Phase 4**: Advanced features and optimization (15 min)

## Testing Requirements

### Backend Testing
- Test all AI agents with various scenarios
- Verify inventory management and alerts
- Test order processing and cart functionality
- Validate chat history persistence

### Frontend Testing  
- Test product loading and filtering
- Verify AI chat functionality across all agent types
- Test cart operations and persistence
- Validate responsive design and error handling

### Integration Testing
- End-to-end user journey testing
- AI agent response quality and context awareness
- Real-time inventory updates
- Cross-browser compatibility

## Configuration Notes

- **AI Integration**: Uses Emergent LLM key for OpenAI GPT-4o-mini
- **Database**: MongoDB with automatic indexing and seeding
- **Session Management**: Browser-based session IDs for cart and chat
- **CORS**: Configured for local development and production deployment
- **Logging**: Comprehensive logging for all AI interactions and business events

The platform is now ready for full integration with real AI-powered ecommerce functionality!