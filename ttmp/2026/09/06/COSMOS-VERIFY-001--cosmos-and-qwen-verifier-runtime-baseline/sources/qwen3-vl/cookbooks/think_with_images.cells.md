## Cell 0 (markdown)

# Cookbook: Think with Images

In this cookbook, we will demonstrate how to think with images through Qwen3-VL inherent `image_zoom_in_tool` and `image_search` function calls using an agent.

## Cell 1 (markdown)

# Install Requirements

We will use [Qwen-Agent](https://github.com/QwenLM/Qwen-Agent) in this book. For demonstration, we need at least the minimal functionality of Qwen-Agent.

## Cell 2 (code)

!pip3 install -U "qwen-agent"
# `pip install -U qwen-agent` will install the minimal requirements.
# The optional requirements, specified in double brackets, are:
#   [gui] for Gradio-based GUI support;
#   [rag] for RAG support;
#   [code_interpreter] for Code Interpreter support;
#   [mcp] for MCP support.

## Cell 3 (markdown)

# Example 1: Zoom-in Assistant

Using DashScope API or local OpenAI server to create an Qwen-Agent that is capable of:
- Thinking, zooming-in (through function call `image_zoom_in_tool`), and analizing.

Notes: the `bbox_2d` for `image_zoom_in_tool` is relative coords with ranging [0, 1000].

## Cell 4 (code)

from qwen_agent.agents import Assistant
from qwen_agent.utils.output_beautify import typewriter_print, multimodal_typewriter_print
# `typewriter_print` prints streaming messages in a non-overlapping manner.

## Cell 5 (code)

llm_cfg = {
    # Use dashscope API
    # 'model': 'qwen3-vl-plus',
    # 'model_server': 'qwenvl_dashscope',
    # 'api_key': '' # **fill your api key here**

    # Use a model service compatible with the OpenAI API, such as vLLM or Ollama:
    'model_type': 'qwenvl_oai',
    'model': 'qwen3-vl-235b-a22b-instruct',
    'model_server': 'http://localhost:8000/v1',  # base_url, also known as api_base
    'api_key': 'EMPTY',
    'generate_cfg': {
        "top_p": 0.8,
        "top_k": 20,
        "temperature": 0.7,
        "repetition_penalty": 1.0,
        "presence_penalty": 1.5
    }
}

analysis_prompt = """Your role is that of a research assistant specializing in visual information. Answer questions about images by looking at them closely and then using research tools. Please follow this structured thinking process and show your work.

Start an iterative loop for each question:

- **First, look closely:** Begin with a detailed description of the image, paying attention to the user's question. List what you can tell just by looking, and what you'll need to look up.
- **Next, find information:** Use a tool to research the things you need to find out.
- **Then, review the findings:** Carefully analyze what the tool tells you and decide on your next action.

Continue this loop until your research is complete.

To finish, bring everything together in a clear, synthesized answer that fully responds to the user's question."""

tools = ['image_zoom_in_tool']
agent = Assistant(
    llm=llm_cfg,
    function_list=tools,
    system_message=analysis_prompt,
    # [!Optional] We provide `analysis_prompt` to enable VL conduct deep analysis. Otherwise use system_message='' to simply enable the tools.
)

## Cell 6 (code)

messages = []
messages += [
    {"role": "user", "content": [
        {"image": "./assets/qwenagent/hopinn.jpg"},
        {"text": "Where was the picture taken?"}
    ]}
]

## Cell 7 (code)

response_plain_text = ''
for ret_messages in agent.run(messages):
    # `ret_messages` will contain all subsequent messages, consisting of interleaved assistant messages and tool responses
    response_plain_text = multimodal_typewriter_print(ret_messages, response_plain_text)

## Cell 8 (markdown)

# Example 2: Multi-functional Assistant

We will create a assistant that is capable of `searching` and `zooming` to show the multi-functionality of VL agent.

To use serper API that enables searching functionality, we need first `export SERPER_API_KEY=xxx` and `export SERPAPI_IMAGE_SEARCH_KEY=xxx` before we run examples in Qwen-Agent.

## Cell 9 (code)

from qwen_agent.agents import Assistant
from qwen_agent.utils.output_beautify import typewriter_print, multimodal_typewriter_print

llm_cfg = {
    # Use dashscope API
    # 'model': 'qwen3-vl-plus',
    # 'model_server': 'qwenvl_dashscope',
    # 'api_key': '' # **fill your api key here**

    # Use a model service compatible with the OpenAI API, such as vLLM or Ollama:
    'model_type': 'qwenvl_oai',
    'model': 'qwen3-vl-235b-a22b-instruct',
    'model_server': 'http://localhost:8000/v1',  # base_url, also known as api_base
    'api_key': 'EMPTY',
    'generate_cfg': {
        "top_p": 0.8,
        "top_k": 20,
        "temperature": 0.7,
        "repetition_penalty": 1.0,
        "presence_penalty": 1.5
    }
}

tools = [
    'image_zoom_in_tool',
    'image_search'
]
agent = Assistant(
    llm=llm_cfg,
    function_list=tools,
    system_message='Use tools to answer.',
)

## Cell 10 (code)

messages = [{
    'role':
        'user',
    'content': [
        {
            'image': 'https://www.gongjiyun.com/assets/QucgbCSISoA7XCxlEI9cVQSOnbd.png'
        },
        {
            'text': 'Find the most prominet feature of these logos and search who creates them.'
        },
    ]
}]

## Cell 11 (code)

response_plain_text = ''
for ret_messages in agent.run(messages):
    # `ret_messages` will contain all subsequent messages, consisting of interleaved assistant messages and tool responses
    response_plain_text = multimodal_typewriter_print(ret_messages, response_plain_text)

## Cell 12 (markdown)

# Use the GUI

We have explored the capabilities of the Qwen-Agent framework and Qwen models in processing files. We can also achieve this by using the GUI.

## Cell 13 (code)

from qwen_agent.gui import WebUI

agent = Assistant(
    name="Qwen File Processing Assistant",
    description="I can help with your file processing needs, ask me anything!",
    llm=llm_cfg,
    function_list=tools
)

WebUI(agent).run()
