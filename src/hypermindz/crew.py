from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from src.hypermindz.tools.custom_tool import (
	query_campaign_metrics, 
	aggregate_performance_data,
	calculate_roi_metrics,
	compare_campaigns,
	get_time_series_data
	)

@CrewBase
class PerformanceCrew():
	"""Hypermindz crew template"""

	agents_config = "config/agents.yaml"
	tasks_config = "config/tasks.yaml"

	@agent
	def performance_analysis_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['performance_analysis_agent'],
			verbose=True
		)

	@agent
	def metrics_aggregate_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['metrics_aggregate_agent'],
			verbose=True,
			tools=[
				query_campaign_metrics, 
				aggregate_performance_data,
				calculate_roi_metrics,
				compare_campaigns,
				get_time_series_data,
			],
		)
	
	@agent
	def insight_generator_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['insight_generator_agent'],
			verbose=True
		)

	@task
	def performance_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['performance_analysis_task'],
			agent=self.performance_analysis_agent(),
		)

	@task
	def metrics_aggregate_task(self) -> Task:
		return Task(
			config=self.tasks_config['metrics_aggregate_task'],
			agent=self.metrics_aggregate_agent(),
		)
	
	@task
	def insight_generator_task(self) -> Task:
		return Task(
			config=self.tasks_config['insight_generator_task'],
			agent=self.insight_generator_agent(),
			output_file='output.md',
		)

	@crew
	def crew(self) -> Crew:
		"""Creates a general crew setup"""
		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical,
		)


