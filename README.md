# 🔍 Developer Tools Research Assistant

An intelligent agentic AI system that automatically researches and compares developer tools using LangChain, Firecrawl, and Streamlit. The system uses a multi-step workflow to extract tools from articles, research each tool individually, and provide detailed comparisons with recommendations.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │ -> │  LangGraph      │ -> │   Firecrawl     │
│   (Frontend)    │    │  Workflow       │    │   (Web Scraper) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              v
                       ┌─────────────────┐
                       │  Gemini 2.5 Pro │
                       │  (LLM Analysis) │
                       └─────────────────┘
```

## 🚀 Features

- **Automated Tool Discovery**: Searches articles to extract relevant developer tools
- **Multi-step Research Pipeline**: Uses LangGraph for structured workflow execution
- **Real-time Progress Updates**: Shows live progress in Streamlit UI
- **Structured Data Extraction**: Uses Pydantic models for consistent data structure
- **Comprehensive Analysis**: Analyzes pricing, tech stack, integrations, and more
- **Smart Recommendations**: Provides tailored suggestions based on analysis

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd developer-tools-research

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## 🔧 Environment Variables

```env
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

## 🏃 Usage

```bash
# Run the Streamlit app
streamlit run app.py

# Navigate to http://localhost:8501
# Enter your query (e.g., "Firebase alternatives")
# Click "Run Analysis"
```

## 🧠 How the Agentic AI Works

### LangGraph Workflow Architecture

The system uses **LangGraph** to create a structured, stateful workflow that processes research queries through multiple coordinated steps. Each step (node) in the graph performs a specific function and passes data to the next step.

```python
# Workflow Structure
extract_tools -> research -> analyze -> END
```

### State Management

The workflow maintains state using the `ResearchState` Pydantic model, which tracks:
- Original query
- Extracted tools list
- Company information
- Search results
- Final analysis

## 📁 File Structure & Component Details

### 1. `models.py` - Data Structure Definition

**Purpose**: Defines Pydantic models for structured data handling and validation.

#### Key Models:

**`CompanyAnalysis`** - Structured output for LLM analysis:
```python
class CompanyAnalysis(BaseModel):
    pricing_model: str  # Free, Freemium, Paid, Enterprise, Unknown
    is_open_source: Optional[bool] = None
    tech_stack: List[str] = []
    description: str = ""
    api_available: Optional[bool] = None
    language_support: List[str] = []
    integration_capabilities: List[str] = []
```

**`CompanyInfo`** - Complete company data structure:
- Stores all research findings about each tool
- Includes developer-specific fields like API availability, language support
- Used for final comparison and recommendations

**`ResearchState`** - Workflow state management:
- Tracks progress through each step
- Maintains extracted tools and company data
- Enables stateful processing in LangGraph

### 2. `firecrawl.py` - Web Scraping Service

**Purpose**: Handles all web scraping operations using Firecrawl API.

#### Key Methods:

**`search_companies(query, num_results)`**:
- Searches the web for relevant articles/pages
- Uses targeted queries like `"{query} company pricing"`
- Returns structured search results with metadata

**`scrape_company_pages(url)`**:
- Scrapes individual company websites
- Converts content to markdown format
- Handles errors gracefully with fallback responses

#### How Firecrawl Works:
1. **Search Phase**: Finds relevant articles about developer tools
2. **Scraping Phase**: Extracts detailed content from each tool's official website
3. **Format Conversion**: Converts HTML to clean markdown for LLM processing
4. **Error Handling**: Manages rate limits and failed requests

### 3. `prompts.py` - LLM Prompt Engineering

**Purpose**: Contains carefully crafted prompts for different analysis phases.

#### Prompt Categories:

**Tool Extraction Prompts**:
- `TOOL_EXTRACTION_SYSTEM`: Instructions for extracting tool names from articles
- `tool_extraction_user()`: Dynamic prompt with article content and query

**Company Analysis Prompts**:
- `TOOL_ANALYSIS_SYSTEM`: Instructions for analyzing developer tools
- `tool_analysis_user()`: Structured analysis prompt for individual tools

**Recommendation Prompts**:
- `RECOMMENDATIONS_SYSTEM`: Instructions for generating final recommendations
- `recommendations_user()`: Comparison and recommendation prompt

#### Prompt Engineering Techniques:
- **Role-based prompts**: Define specific roles (tech researcher, senior engineer)
- **Structured output**: Guide LLM to produce consistent data formats
- **Context limitation**: Truncate content to fit LLM context windows
- **Example-driven**: Provide clear output format examples

### 4. `workflow.py` - Core Agentic AI Logic

**Purpose**: Orchestrates the entire research pipeline using LangGraph.

#### Workflow Steps Breakdown:

### Step 1: `_extract_tools_step()`

**Objective**: Find and extract specific developer tools from articles.

**Process**:
1. **Article Search**: Query Firecrawl for articles about the topic
   ```python
   article_query = f"{state.query} tools comparison best alternatives"
   search_results = self.firecrawl.search_companies(article_query, num_results=3)
   ```

2. **Content Aggregation**: Scrape and combine content from multiple articles
   ```python
   all_content += scraped.markdown[:1500] + "\n\n"
   ```

3. **Tool Extraction**: Use LLM to extract specific tool names
   ```python
   messages = [
       SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
       HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content))
   ]
   ```

4. **Output Processing**: Clean and format extracted tool names
   ```python
   tool_names = [name.strip() for name in response.content.strip().split("\n") if name.strip()]
   ```

**Why This Step**: Articles often contain comprehensive lists of alternatives and comparisons, making them ideal sources for tool discovery.

### Step 2: `_research_step()`

**Objective**: Research each extracted tool individually for detailed information.

**Process**:
1. **Tool Validation**: Check if tools were successfully extracted
2. **Individual Research**: For each tool:
   - Search for official website
   - Scrape detailed content
   - Analyze using structured LLM prompts
3. **Data Structuring**: Convert analysis into `CompanyInfo` objects
4. **Progress Tracking**: Update UI with research progress

**Key Function - `_analyze_company_content()`**:
```python
def _analyze_company_content(self, company_name: str, content: str) -> CompanyAnalysis:
    structured_llm = self.llm.with_structured_output(CompanyAnalysis)
    # ... analysis logic
```

**Structured Output**: Uses Pydantic models to ensure consistent data extraction:
- Pricing model classification
- Open source detection
- Tech stack identification
- API availability assessment
- Language support analysis
- Integration capabilities

### Step 3: `_analyze_step()`

**Objective**: Generate final recommendations based on all research data.

**Process**:
1. **Data Aggregation**: Combine all company research into single context
2. **Comparative Analysis**: Use LLM to compare tools and generate recommendations
3. **Structured Output**: Provide concise, actionable recommendations

**LLM Reasoning**: The final step uses the complete research dataset to:
- Compare pricing models
- Identify best use cases
- Highlight technical advantages
- Provide implementation recommendations

### 5. `app.py` - Streamlit Frontend

**Purpose**: Provides user interface with real-time progress updates.

#### Key Features:

**Progress Visualization**:
- Real-time step updates
- Progress bar with completion percentage
- Success/error indicators

**Results Display**:
- Summary metrics (tools found, open source count, etc.)
- Final recommendations
- Detailed tool comparison in expandable sections

**Progress Callback System**:
```python
result = workflow.run(query, progress_callback={
    'step1': step1_placeholder,
    'step2': step2_placeholder, 
    'step3': step3_placeholder,
    'progress_bar': progress_bar
})
```

## 🔄 Complete Workflow Example

### Input Query: "Firebase alternatives"

**Step 1 - Tool Extraction**:
1. Search for articles about "Firebase alternatives tools comparison"
2. Scrape content from top 3 articles
3. Extract tool names: `["Supabase", "Appwrite", "AWS Amplify", "Nhost", "Back4App"]`

**Step 2 - Individual Research**:
1. For each tool (e.g., Supabase):
   - Search: "Supabase official site"
   - Scrape: https://supabase.com
   - Analyze: Extract pricing, tech stack, features
   - Structure: Create CompanyInfo object

**Step 3 - Comparative Analysis**:
1. Aggregate all research data
2. Compare features, pricing, use cases
3. Generate recommendation: "Supabase is best for PostgreSQL-based projects..."

## 🎯 Agentic AI Principles Used

### 1. **Autonomous Decision Making**
- The system decides which tools to research based on extracted data
- Adapts search strategies if initial extraction fails
- Makes contextual decisions about data prioritization

### 2. **Multi-Step Reasoning**
- Each step builds on previous results
- Maintains context across the entire workflow
- Uses intermediate results to inform subsequent steps

### 3. **Structured Output Generation**
- Uses Pydantic models for consistent data structure
- Employs structured LLM outputs for reliable parsing
- Maintains data integrity across workflow steps

### 4. **Error Handling & Adaptation**
- Graceful fallbacks when extraction fails
- Continues processing with partial results
- Provides meaningful error messages to users

### 5. **State Management**
- Tracks workflow progress through ResearchState
- Maintains data persistence across steps
- Enables resumable and debuggable workflows

## 🛠️ Technical Implementation Details

### LangGraph Integration

**Graph Definition**:
```python
graph = StateGraph(ResearchState)
graph.add_node("extract_tools", self._extract_tools_step)
graph.add_node("research", self._research_step)
graph.add_node("analyze", self._analyze_step)
graph.set_entry_point("extract_tools")
graph.add_edge("extract_tools", "research")
graph.add_edge("research", "analyze")
graph.add_edge("analyze", END)
```

**State Updates**: Each step returns a dictionary that updates the workflow state:
```python
return {"extracted_tools": tool_names}  # Updates ResearchState.extracted_tools
```

### Gemini Integration

**Model Configuration**:
```python
self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
```

**Structured Output**:
```python
structured_llm = self.llm.with_structured_output(CompanyAnalysis)
```

### Error Handling Strategy

1. **Network Errors**: Graceful fallbacks for failed web requests
2. **LLM Errors**: Default values for failed analysis
3. **Data Validation**: Pydantic models ensure data integrity
4. **User Feedback**: Clear error messages in UI

## 📊 Data Flow Diagram

```
User Query
    ↓
Article Search (Firecrawl)
    ↓
Tool Extraction (Gemini)
    ↓
Individual Tool Research (Firecrawl + Gemini)
    ↓
Comparative Analysis (Gemini)
    ↓
Structured Results (Pydantic)
    ↓
UI Display (Streamlit)
```

## 🔍 Advanced Features

### Dynamic Progress Updates
- Real-time UI updates during processing
- Step-by-step progress indication
- Error state visualization

### Content Optimization
- Intelligent content truncation for LLM context limits
- Markdown formatting for better LLM processing
- Targeted search queries for better results

### Scalable Architecture
- Modular component design
- Easy to extend with new analysis steps
- Configurable parameters for different use cases

## 🤖 AI Agent Capabilities

This system demonstrates several key agentic AI capabilities:

1. **Planning**: Structures research into logical steps
2. **Execution**: Carries out complex multi-step workflows
3. **Adaptation**: Adjusts strategy based on intermediate results
4. **Reasoning**: Makes informed decisions about tool comparisons
5. **Communication**: Provides clear, actionable recommendations

## 📈 Performance Considerations

- **Rate Limiting**: Handles API rate limits gracefully
- **Content Optimization**: Truncates content to fit LLM context
- **Concurrent Processing**: Could be enhanced with async processing
- **Caching**: Could implement result caching for repeated queries

## 🚀 Future Enhancements

- **Parallel Processing**: Research multiple tools simultaneously
- **Enhanced Filtering**: More sophisticated tool selection criteria
- **Historical Tracking**: Track tool popularity and trends over time
- **Custom Scoring**: Implement weighted scoring for different criteria
- **API Integration**: Direct integration with tool APIs for real-time data

## 🔧 Troubleshooting

**Common Issues**:
- **Missing API Keys**: Ensure environment variables are set
- **Rate Limiting**: Reduce number of tools researched simultaneously
- **Memory Issues**: Implement content truncation for large articles
- **Network Errors**: Add retry logic for failed requests

## 📝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain/LangGraph**: For workflow orchestration
- **Firecrawl**: For web scraping capabilities
- **Google Gemini**: For LLM analysis
- **Streamlit**: For rapid UI development
- **Pydantic**: For data validation and structure