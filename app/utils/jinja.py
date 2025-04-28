from jinja2 import Template


async def render_template(template_string: str, context: dict) -> str:
    if context:
        template = Template(template_string)
        return template.render(context)
    else:
        return template_string
