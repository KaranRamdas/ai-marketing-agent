# main.py
from crewai import Agent, Task, Crew, Process
# from langchain_openai import ChatOpenAI
from tools.metric_calculator import calculate_marketing_metrics
from tools.campaign_comparator import compare_campaigns
from tools.roi_calculator import calculate_roi
from tools.trend_analyzer import analyze_trends
from tools.anomaly_detector import detect_anomalies
from tools.budget_recommender import recommend_budget_allocation

# ============================================================================
# DEFINE TOOLS FOR THE AGENT
# ============================================================================

tools = [
    calculate_marketing_metrics,
    compare_campaigns,
    calculate_roi,
    analyze_trends,
    detect_anomalies,
    recommend_budget_allocation
]

# ============================================================================
# CREATE THE MARKETING ANALYST AGENT
# ============================================================================

analyst_agent = Agent(
    role="Marketing Analytics Specialist",
    goal="Analyze marketing campaign performance and provide actionable insights",
    backstory="""You are an expert marketing analyst with 10 years of experience.
    You specialize in analyzing campaign performance, identifying trends, and
    recommending budget allocation strategies. You have deep knowledge of marketing
    metrics like CTR, CPC, ROAS, ROI, and conversion rates. Your job is to help
    marketing teams understand their campaign performance and make data-driven decisions.""",
    tools=tools,
    # llm=ChatOpenAI(model_name="gpt-3.5-turbo"),
    verbose=True,
    allow_delegation=False
)

# ============================================================================
# CREATE TASKS
# ============================================================================

def create_analysis_task(description: str) -> Task:
    """Create a task for the analyst agent"""
    return Task(
        description=description,
        agent=analyst_agent,
        expected_output="Detailed analysis with insights and recommendations"
    )

# ============================================================================
# EXAMPLE TASKS (Uncomment to use)
# ============================================================================

task1 = create_analysis_task(
    """Analyze the performance of all marketing campaigns over the past 90 days.
    Calculate key metrics (CTR, CPC, RPC, ROAS, conversion rate) for each campaign
    using the data in data/marketing_campaigns_production.csv.
    Provide a summary of which campaigns are performing best."""
)

task2 = create_analysis_task(
    """Compare Growth Campaign A and Growth Campaign B. Which one performs better?
    Show the metrics for each campaign and identify the winner by key performance indicators.
    Data file: data/marketing_campaigns_production.csv"""
)

task3 = create_analysis_task(
    """Calculate the ROI for all campaigns in data/marketing_campaigns_production.csv.
    Show total revenue, total ad spend, net profit, ROI percentage, and payback period
    for each campaign. Which campaign has the best ROI?"""
)

task4 = create_analysis_task(
    """Analyze the trend of ROAS (Return on Ad Spend) for all campaigns in
    data/marketing_campaigns_production.csv. Is ROAS improving, declining, or stable?
    What are your recommendations based on the trend?"""
)

task5 = create_analysis_task(
    """Detect any anomalies in the Email Blast campaign's performance using
    data/marketing_campaigns_production.csv. Look for unusual spikes or dips
    in ROAS. What insights can you provide about these anomalies?"""
)

task6 = create_analysis_task(
    """Recommend how to allocate a $100,000 marketing budget across all campaigns
    in data/marketing_campaigns_production.csv based on their ROAS performance.
    Which campaigns should we scale, maintain, or pause?"""
)

# ============================================================================
# CREATE CREW AND RUN
# ============================================================================

def run_single_analysis(task: Task):
    """Run a single analysis task"""
    crew = Crew(
        agents=[analyst_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    return result

def run_comprehensive_analysis():
    """Run all analysis tasks in sequence"""
    crew = Crew(
        agents=[analyst_agent],
        tasks=[task1, task2, task3, task4, task5, task6],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    return result

# ============================================================================
# INTERACTIVE MODE
# ============================================================================

def interactive_mode():
    """Allow user to ask questions to the agent"""
    print("\n" + "=" * 70)
    print("🤖 MARKETING ANALYTICS AGENT - INTERACTIVE MODE")
    print("=" * 70)
    print("Ask me anything about your marketing campaigns!")
    print("Examples:")
    print("  - 'What is the CTR for Growth Campaign A?'")
    print("  - 'Compare Email Blast vs Retargeting Campaign'")
    print("  - 'Which campaign has the best ROI?'")
    print("  - 'Analyze trends for all campaigns'")
    print("  - 'Detect anomalies in campaign performance'")
    print("  - 'How should I allocate my marketing budget?'")
    print("\nType 'exit' to quit.\n")
    
    while True:
        user_input = input("📊 Your question: ").strip()
        
        if user_input.lower() == 'exit':
            print("Goodbye! 👋")
            break
        
        if not user_input:
            continue
        
        # Create a task from user input
        user_task = create_analysis_task(
            f"""Answer the following question about the marketing campaigns in
            data/marketing_campaigns_production.csv:
            
            {user_input}"""
        )
        
        # Run the analysis
        print("\n🔍 Analyzing...\n")
        result = run_single_analysis(user_task)
        print(f"\n✅ Analysis Result:\n{result}\n")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 MARKETING ANALYTICS AGENT SYSTEM")
    print("=" * 70)
    print("\nSelect an option:")
    print("1. Run Task 1: Analyze all campaigns")
    print("2. Run Task 2: Compare two campaigns")
    print("3. Run Task 3: Calculate ROI")
    print("4. Run Task 4: Analyze trends")
    print("5. Run Task 5: Detect anomalies")
    print("6. Run Task 6: Budget recommendations")
    print("7. Run all tasks (comprehensive)")
    print("8. Interactive mode (ask questions)")
    print("9. Exit")
    
    choice = input("\nEnter your choice (1-9): ").strip()
    
    if choice == "1":
        print("\n📊 Running Task 1: Analyze all campaigns...\n")
        result = run_single_analysis(task1)
        print(f"\n{result}")
    
    elif choice == "2":
        print("\n🔄 Running Task 2: Compare campaigns...\n")
        result = run_single_analysis(task2)
        print(f"\n{result}")
    
    elif choice == "3":
        print("\n💰 Running Task 3: Calculate ROI...\n")
        result = run_single_analysis(task3)
        print(f"\n{result}")
    
    elif choice == "4":
        print("\n📈 Running Task 4: Analyze trends...\n")
        result = run_single_analysis(task4)
        print(f"\n{result}")
    
    elif choice == "5":
        print("\n🎯 Running Task 5: Detect anomalies...\n")
        result = run_single_analysis(task5)
        print(f"\n{result}")
    
    elif choice == "6":
        print("\n💡 Running Task 6: Budget recommendations...\n")
        result = run_single_analysis(task6)
        print(f"\n{result}")
    
    elif choice == "7":
        print("\n🔥 Running comprehensive analysis (all 6 tasks)...\n")
        result = run_comprehensive_analysis()
        print(f"\n{result}")
    
    elif choice == "8":
        interactive_mode()
    
    elif choice == "9":
        print("Goodbye! 👋")
    
    else:
        print("Invalid choice. Please enter 1-9.")