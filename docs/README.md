# Social Media Content Manager - UX Mockups

## 📋 Overview

These are interactive HTML mockups for validating the UX of the Social Media Content Manager application before development.

## 🚀 How to View

1. Open `index.html` in your web browser
2. Click on any view card to explore that section
3. Navigate between views using the top navigation bar
4. Click "Back to Mockups" button (bottom-right) to return to the main index

## 📱 Available Views

### 1. **Dashboard** (`dashboard.html`)
- Overview of active projects and recent activity
- Quick stats (active projects, assets created, hot quota, pending validations)
- Recent projects list with status
- Mini calendar preview
- Notifications panel
- Quick actions buttons

### 2. **My Projects** (`projects.html`)
- Complete list of all projects (cold & hot content)
- Advanced filtering (type, brand, status, platform)
- Project status tracking through workflow stages
- Sortable and searchable table view
- Pagination

### 3. **Project Detail** (`project-detail.html`)
- Complete project information
- Visual workflow progress tracker (9 stages)
- Brief & description
- Assets & files with links to Box/SharePoint
- Copy guidelines for markets
- Market adoption tracking
- Activity timeline
- Team members
- Quick actions

### 4. **Editorial Calendar** (`calendar.html`)
- Monthly calendar view
- Filters by market, brand, type, platform, format
- Hot content quota tracker with progress bar
- Color-coded content (Hot/Cold/Paid)
- Interactive calendar cells
- Legend for content types

### 5. **Global Library** (`library.html`)
- Browse all Global team content
- Adoption statistics
- Filter by brand, type, platform, adoption status
- Card-based grid layout
- Visual adoption indicators (market badges)
- "Mark as Interested" / "View Details" actions
- NEW badges for recent content

### 6. **Newsroom** (`newsroom.html`)
- Weekly hot trends discussion platform
- Next meeting information banner
- Tabs: Pending Discussion, Approved, Rejected, Archive
- Priority levels (High/Medium/Low)
- Team voting system
- Comments and discussions
- Trend references and links
- Approve/Discuss/Reject actions

### 7. **Reporting** (`reporting.html`)
- Key metrics dashboard
- Global adoption rate by market (with progress bars)
- Adoption rate by brand
- Monthly production statistics table
- Consolidated calendar overview (all markets)
- Export functionality
- Insights and recommendations

## 🎨 Design Features

- **Responsive Design**: Built with Tailwind CSS
- **Color Coding**:
  - Blue: Cold Content / France
  - Red: Hot Content
  - Purple: Paid Content / Global
  - Green: South Europe / Approved
  - Orange: North America / Pending
  - Yellow: Babybel brand
  - And more...

- **Interactive Elements**: Buttons, filters, tabs (visual only - no functionality)
- **Icons**: SVG icons throughout for better UX
- **Status Badges**: Visual status indicators for projects, trends, adoptions

## 📝 Key Workflow

The mockups demonstrate the complete workflow:

1. **Cold Content**: Brief → Ideation → Client Presentation → Correction → Market Presentation → Creation → Revision → Client Validation → Distributed
2. **Hot Content**: Spotted → Newsroom Discussion → Approved → Creation → Published
3. **Global Library**: Created by Global → Visible to Markets → Markets Adopt → Markets Adapt

## 🔍 What to Validate

When reviewing these mockups, consider:

1. **Navigation**: Is it easy to move between sections?
2. **Information Architecture**: Is information logically organized?
3. **Workflow Clarity**: Are workflow stages clear?
4. **Filters & Search**: Are filtering options sufficient?
5. **Visual Hierarchy**: Is important information prominent?
6. **Actions**: Are CTAs (buttons) clear and well-placed?
7. **Data Visualization**: Are stats and charts understandable?
8. **Collaboration Features**: Do voting/comments/adoptions make sense?

## 📦 Files Structure

```
mockups/
├── index.html          # Main landing page with navigation
├── dashboard.html      # Dashboard view
├── projects.html       # Projects list view
├── project-detail.html # Single project detail view
├── calendar.html       # Editorial calendar view
├── library.html        # Global library view
├── newsroom.html       # Newsroom/trends view
├── reporting.html      # Analytics & reporting view
└── README.md          # This file
```

## ⚠️ Important Notes

- These are **static mockups** - buttons and links are for visual reference only
- No backend functionality is implemented
- Data shown is sample/dummy data for demonstration
- The mockups use Tailwind CSS via CDN (requires internet connection)
- Best viewed in modern browsers (Chrome, Firefox, Safari, Edge)

## 🎯 Next Steps

After validation:

1. Gather feedback on UX/UI
2. Identify improvements or missing features
3. Prioritize features for development
4. Create technical specifications
5. Begin development with approved design

## 📞 Questions?

If you have questions or suggestions about the mockups, please document them for discussion.

---

**Created**: November 2025
**Version**: 1.0
**Status**: Ready for UX validation
