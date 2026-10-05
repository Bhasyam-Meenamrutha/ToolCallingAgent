import os
import ssl

from dotenv import load_dotenv
from google import genai
from google.genai import types

from weather_tool import get_weather
from github_tool import get_github_user, get_repo_info


# ============================================================
# 1. Load API key
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from .env")


# ============================================================
# 2. DEV/TEST ONLY - Disable SSL verification
# ============================================================

unverified_ssl_context = ssl.create_default_context()

unverified_ssl_context.check_hostname = False
unverified_ssl_context.verify_mode = ssl.CERT_NONE


http_options = types.HttpOptions(
    client_args={
        "verify": unverified_ssl_context
    },
    async_client_args={
        "verify": unverified_ssl_context
    }
)


# ============================================================
# 3. Create Gemini client
# ============================================================

client = genai.Client(
    api_key=api_key,
    http_options=http_options
)

MODEL = "gemini-3.5-flash-lite"



# ============================================================
# 4. WEATHER TOOL
# ============================================================

weather_function = types.FunctionDeclaration(
    name="get_weather",

    description=(
        "Get current weather information for a city. "
        "Use this tool when the user asks about current "
        "weather, temperature, humidity, rainfall, or wind."
    ),

    parameters=types.Schema(
        type=types.Type.OBJECT,

        properties={
            "city": types.Schema(
                type=types.Type.STRING,
                description="Name of the city"
            )
        },

        required=["city"]
    )
)


# ============================================================
# 5. GITHUB USER TOOL
# ============================================================

github_user_function = types.FunctionDeclaration(
    name="get_github_user",

    description=(
        "Get public GitHub profile information for a user, "
        "including username, public repositories, followers, "
        "following, and GitHub profile URL."
    ),

    parameters=types.Schema(
        type=types.Type.OBJECT,

        properties={
            "username": types.Schema(
                type=types.Type.STRING,
                description="GitHub username"
            )
        },

        required=["username"]
    )
)


# ============================================================
# 6. GITHUB REPOSITORY TOOL
# ============================================================

github_repo_function = types.FunctionDeclaration(
    name="get_repo_info",

    description=(
        "Get public information about a GitHub repository, "
        "including stars, forks, open issues, programming "
        "language, description, and repository URL."
    ),

    parameters=types.Schema(
        type=types.Type.OBJECT,

        properties={
            "owner": types.Schema(
                type=types.Type.STRING,
                description="GitHub username or organization"
            ),

            "repo": types.Schema(
                type=types.Type.STRING,
                description="GitHub repository name"
            )
        },

        required=["owner", "repo"]
    )
)


# ============================================================
# 7. REGISTER ALL TOOLS
# ============================================================

tools = types.Tool(
    function_declarations=[
        weather_function,
        github_user_function,
        github_repo_function
    ]
)


# ============================================================
# 8. START AGENT
# ============================================================

print("========================================")
print("       GEMINI MULTI-TOOL AGENT")
print("========================================")

print("Available Tools:")
print("1. get_weather()")
print("2. get_github_user()")
print("3. get_repo_info()")
print()
print("Type 'exit' to stop.")
print()


while True:

    user_prompt = input("You: ").strip()

    if user_prompt.lower() == "exit":
        print("Bot: Goodbye!")
        break

    if not user_prompt:
        continue

    try:

        # ====================================================
        # STEP 1: Ask Gemini
        # ====================================================

        response = client.models.generate_content(

            model=MODEL,

            contents=user_prompt,

            config=types.GenerateContentConfig(
                tools=[tools]
            )
        )


        # ====================================================
        # STEP 2: Check for tool calls
        # ====================================================

        function_calls = response.function_calls


        if function_calls:

            print("\n----------------------------------------")
            print("TOOL CALL DETECTED")
            print("----------------------------------------")


            tool_response_parts = []


            # =================================================
            # STEP 3: Execute requested tools
            # =================================================

            for function_call in function_calls:

                print("Tool:", function_call.name)

                print("Arguments:", function_call.args)


                if function_call.name == "get_weather":

                    city = function_call.args["city"]

                    print("\nExecuting get_weather()...")

                    tool_result = get_weather(city)


                elif function_call.name == "get_github_user":

                    username = function_call.args["username"]

                    print("\nExecuting get_github_user()...")

                    tool_result = get_github_user(username)


                elif function_call.name == "get_repo_info":

                    owner = function_call.args["owner"]

                    repo = function_call.args["repo"]

                    print("\nExecuting get_repo_info()...")

                    tool_result = get_repo_info(
                        owner,
                        repo
                    )


                else:

                    tool_result = {
                        "success": False,
                        "message": "Unknown tool"
                    }


                print("Tool Result:", tool_result)


                # =================================================
                # STEP 4: Create tool response
                # =================================================

                tool_response_parts.append(
                    types.Part.from_function_response(
                        name=function_call.name,
                        response=tool_result
                    )
                )


            # =================================================
            # STEP 5: Send result back to Gemini
            # =================================================

            final_response = client.models.generate_content(

                model=MODEL,

                contents=[
                    user_prompt,
                    response.candidates[0].content,
                    *tool_response_parts
                ],

                config=types.GenerateContentConfig(
                    tools=[tools]
                )
            )


            # =================================================
            # STEP 6: Final answer
            # =================================================

            print("\n----------------------------------------")
            print("FINAL ANSWER")
            print("----------------------------------------")

            print("Bot:", final_response.text)
            print()


        else:

            # =================================================
            # No tool required
            # =================================================

            print("\nBot:", response.text)
            print()


    except Exception as e:

        print("\n----------------------------------------")
        print("ERROR")
        print("----------------------------------------")

        print(e)

        print()