from jinja2 import Template

class Reporter:
    def __init__(self):
        self.template = Template("""
            <h1>LLM Updates</h1>
            <ul>
                {% for update in updates %}
                    <li>{{ update }}</li>
                {% endfor %}
            </ul>
        """)

    def generate_report(self, updates):
        return self.template.render(updates=updates)
