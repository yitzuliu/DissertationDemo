# Frontend Documentation

## Overview

The frontend is a web-based interface for the AI Manual Assistant system, providing real-time interaction with the dual-loop memory system. It consists of two main pages: the main interface (`index.html`) and the query interface (`query.html`).

## Architecture

### File Structure
```
src/frontend/
├── index.html              # Main interface with camera and chat
├── query.html              # Dedicated query interface
├── old_index.html          # Legacy main interface
├── Fileindex.html          # File upload interface
├── assets/                 # Static assets
│   └── icons/             # Icon files
├── css/                   # Stylesheets
│   ├── main.css           # Main styles
│   ├── components.css     # Component-specific styles
│   └── responsive.css     # Responsive design styles
├── js/                    # JavaScript modules
│   ├── main.js            # Main application logic
│   ├── camera.js          # Camera management
│   ├── query.js           # Query interface logic
│   ├── components/        # Reusable components
│   │   ├── api.js         # API communication
│   │   ├── camera.js      # Camera component
│   │   ├── tabs.js        # Tab management
│   │   └── ui.js          # UI utilities
│   └── utils/             # Utility functions
│       ├── config.js      # Configuration management
│       └── helpers.js     # Helper functions
└── README.md              # This file
```

## Pages

### Main Interface (`index.html`)

The main interface provides:
- **Camera Integration**: Real-time video capture for VLM observations
- **Chat Interface**: Direct communication with the AI system
- **Start/Stop Controls**: Manual control over the subconscious loop
- **Status Display**: Real-time system status and feedback

#### Key Features:
- Camera stream management
- Image capture and processing
- Chat completion requests
- System status monitoring
- Responsive design

### Query Interface (`query.html`)

The query interface provides:
- **Instant Query Processing**: Direct access to the State Tracker
- **Query Examples**: Pre-defined query templates
- **Response Display**: Formatted response output
- **Performance Metrics**: Processing time and confidence scores

#### Key Features:
- Real-time query processing
- Query type classification
- Detailed response formatting
- Connection status monitoring
- Performance tracking

## Components

### JavaScript Modules

#### `main.js`
- Main application initialization
- Event handling and coordination
- System state management

#### `camera.js`
- Camera stream management
- Image capture and processing
- Video frame handling

#### `query.js`
- Query interface logic
- API communication for queries
- Response formatting and display
- Error handling

#### `components/api.js`
- HTTP request handling
- API endpoint communication
- Response processing

#### `components/camera.js`
- Camera component logic
- Video stream management
- Image capture utilities

#### `components/tabs.js`
- Tab switching logic
- Content management
- UI state coordination

#### `components/ui.js`
- UI utility functions
- DOM manipulation helpers
- Animation and effects

#### `utils/config.js`
- Configuration loading
- Environment settings
- API endpoint configuration

#### `utils/helpers.js`
- General utility functions
- Data formatting helpers
- Common operations

### CSS Modules

#### `main.css`
- Global styles and variables
- Layout and typography
- Color scheme and theming

#### `components.css`
- Component-specific styles
- Interactive elements
- Form styling

#### `responsive.css`
- Mobile-first responsive design
- Breakpoint management
- Adaptive layouts

## API Integration

### Backend Communication

The frontend communicates with the backend through several endpoints:

#### Main Interface Endpoints:
- `POST /api/v1/chat/completions` - Chat completion requests
- `POST /api/v1/state/process` - VLM observation processing

#### Query Interface Endpoints:
- `POST /api/v1/state/query` - Instant query processing
- `GET /api/v1/state/query/capabilities` - Query capabilities

### Data Flow

1. **Camera Stream**: Continuous video capture
2. **Image Processing**: Frame capture and preprocessing
3. **VLM Communication**: Image sent to model service
4. **State Tracking**: Observations processed by State Tracker
5. **User Queries**: Direct access to current state
6. **Response Display**: Formatted responses to user

## Features

### Real-time Processing
- Continuous camera stream processing
- Instant query response
- Live status updates

### Error Handling
- Network error recovery
- Service connection monitoring
- User-friendly error messages

### Performance Optimization
- Efficient image processing
- Optimized API calls
- Responsive UI updates

### User Experience
- Intuitive interface design
- Clear status indicators
- Helpful query examples

## Configuration

### Environment Variables
- `API_BASE_URL`: Backend API base URL
- `MODEL_SERVICE_URL`: Model service URL
- `DEBUG_MODE`: Debug logging enable/disable

### Browser Requirements
- Modern browser with WebRTC support
- Camera access permissions
- JavaScript enabled

## Development

### Setup
1. Ensure backend services are running
2. Open `index.html` or `query.html` in a web browser
3. Grant camera permissions when prompted
4. Start the subconscious loop for full functionality

### Testing
- Use the query interface for testing State Tracker responses
- Monitor browser console for debugging information
- Check network tab for API communication

### Debugging
- Browser developer tools for frontend debugging
- Console logging for JavaScript debugging
- Network monitoring for API communication

## Troubleshooting

### Common Issues

#### Camera Not Working
- Check browser permissions
- Ensure HTTPS or localhost
- Verify camera hardware

#### API Connection Errors
- Verify backend services are running
- Check API endpoint configuration
- Monitor network connectivity

#### Query Response Issues
- Check State Tracker service status
- Verify query format
- Monitor response formatting

### Performance Issues
- Monitor browser performance
- Check API response times
- Optimize image processing

## Future Enhancements

### Planned Features
- Enhanced UI animations
- Advanced query templates
- Real-time collaboration
- Mobile app version

### Technical Improvements
- Progressive Web App (PWA) support
- Offline functionality
- Advanced caching strategies
- Performance optimizations

## Contributing

When contributing to the frontend:

1. Follow the existing code structure
2. Maintain responsive design principles
3. Test across different browsers
4. Update documentation as needed
5. Ensure accessibility compliance

## License

This frontend is part of the AI Manual Assistant system and follows the same licensing terms as the main project.
