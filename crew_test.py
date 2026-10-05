from crewai import Agent, Task, Crew, LLM

architect_llm = LLM(model="ollama/qwen3:8b", base_url="http://127.0.0.1:11434")
coder_llm = LLM(model="ollama/deepseek-coder:6.7b", base_url="http://127.0.0.1:11435")

print("ARCHITECT:", vars(architect_llm))
print("CODER:", vars(coder_llm))

architect = Agent(
    role="Arkitekt",
    goal="Beskriv en simpel komponent-opdeling for en to-do liste-app",
    backstory="En erfaren softwarearkitekt der taenker i moduler og ansvar.",
    llm=architect_llm,
    verbose=True,
)

coder = Agent(
    role="Udvikler",
    goal="Skriv Python-kode ud fra arkitektens beskrivelse",
    backstory="En pragmatisk Python-udvikler.",
    llm=coder_llm,
    verbose=True,
)

architecture_task = Task(
    description="Beskriv en simpel komponent-opdeling (3 bullets) for en to-do liste-app.",
    expected_output="3 bullet points med komponentnavne og ansvar.",
    agent=architect,
)

coding_task = Task(
    description="Skriv en Python-funktion der tilfoejer en opgave til en liste, baseret paa arkitektens output.",
    expected_output="Python-kode i en kodeblok.",
    agent=coder,
    context=[architecture_task],
)

crew = Crew(agents=[architect, coder], tasks=[architecture_task, coding_task], verbose=True)
result = crew.kickoff()
print(result)