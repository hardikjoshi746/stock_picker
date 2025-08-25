from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field
from typing import List
from stock_picker.tools.push_tool import PushNotificationTool
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

class TrendingCompany(BaseModel):
    """Represents a trending company in the news"""
    name: str = Field(description="Name of the company")
    ticker: str = Field(description="Stock ticker symbol")
    reason: str = Field(description="Reason why the company is trending")

class TrendingCompanyList(BaseModel):
    """Represents a list of trending companies"""
    companies: List[TrendingCompany] = Field(description="List of trending companies")

class TrendingCompanyResearch(BaseModel):
    """Detailed research of a company"""
    name: str = Field(description="Name of the company")
    market_position: str = Field(description="Current market position and competitive analysis")
    future_outlook: str = Field(description="Future outlook and growth potential")
    investment_potential: str = Field(description="Investment potential and sustainability for investment")

class TrendingCompanyResearchList(BaseModel):
    """Represents a list of research data for trending companies"""
    research: List[TrendingCompanyResearch] = Field(description="Comprehensive research on all trending companies")

@CrewBase
class StockPicker():
    """StockPicker crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(config=self.agents_config['trending_company_finder'], tools=[SerperDevTool()])

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(config=self.agents_config['financial_researcher'], tools=[SerperDevTool()])
    
    @agent
    def stock_picker(self) -> Agent:
        return Agent(config=self.agents_config['stock_picker'], tools=[PushNotificationTool()])

    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'], 
            output_pydantic=TrendingCompanyList)
    
    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'], 
            output_pydantic=TrendingCompanyResearchList)
    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'],
        )
    
    @crew
    def crew(self) -> Crew:
        """Create the stock picker crew"""
        manager = Agent(
            config = self.agents_config['manager'],
            allow_delegation = True
        )
        return Crew(
            agents = self.agents,
            tasks = self.tasks,
            process = Process.hierarchical,
            verbose = True,
            manager_agent = manager
        )
