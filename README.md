
# Task

Develop a QQ channel bot using the qq-botpy library in Python. The bot adopts a file-driven design with the following functionalities:

1. Passive Reply: When mentioned in a channel, parse the user's command, read the corresponding content from a local file, and reply.

2. Proactive Push: Implement a background task to periodically/schedule scanning of a specific directory and proactively send prepared file content to a designated group chat.

# Design Requirements:

## Framework Structure:

* Must be based on qq-botpy. The core is to create a class that inherits from botpy.Client and implement the `async def on_at_message_create(self, message):` method to handle @ messages.
	* Related content references: https://github.com/tencent-connect/botpy and https://bot.q.qq.com/wiki/develop/

* File-driven and data scraping classes:

	* All message content to be sent is stored as files in the project's `./data` directory.

	* Consider reasonable inheritance for all data scraping classes, as scraping methods and variations are numerous.

	* File naming rules: Files starting with "P_" indicate "publishable". For example:

	`./data/P_atcoder.txt` stores formatted AtCoder competition information.

	`./data/P_codeforces.txt` stores formatted Codeforces competition information, which can be obtained through the official API.

	`./data/P_weather.txt` stores formatted weather information.

* Logical judgment: In the `on_at_message_create` method, judge the user message.

	* For example, if the message contains "cf", read the contents of `./data/P_codeforces.txt` and reply.

	* If the message contains "at", read the contents of `./data/P_atcoder.txt` and reply.

* Active sending: In the robot client class, create an asynchronous background task (e.g., using `asyncio.create_task`). * This task runs in a loop (e.g., while True: with await asyncio.sleep(60)), checking every minute for new files in the ./data/ directory that conform to a specific naming rule (e.g., starting with A_).

	* If found, it reads the file content and calls self.api.post_message to send it to the preset channel ID.




Please provide a complete, runnable Python code implementation. The code should include:

1. The robot client class definition.

2. The logic for passive replies (on_at_message_create).

3. The implementation and startup of the background task for proactive push.

4. Correct intents settings and client.run startup logic.

5. The data scraping class.
