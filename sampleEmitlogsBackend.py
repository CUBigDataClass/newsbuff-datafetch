# sample file that uses emitlogsBackend.py to publish backend logs to rabbitMQ backend queue - For reference

# Step 1: Import emitlogsBackend python file
import emitlogsBackend

# Step 2: Use two variables <var1> and <var2> to fetch connection and rabbitMQ details
rabbitMQChannel, rabbitMQ = emitlogsBackend.fetchConnection()

# Step 3: Use respective function calls to publish your respective info/debug/warning log messages into rabbitMQ backend queue 
#         by passing the parameters <log message> and <var1> obtained in Step 2
emitlogsBackend.log_info("Your info message - sample run example - info", rabbitMQChannel)
emitlogsBackend.log_debug("Your debug message - sample run - debug", rabbitMQChannel)
emitlogsBackend.log_warning("Your warning message - sample run - warning", rabbitMQChannel)

# Step 4: Close the channel connection using the following function by passing <var2> from Step 2
emitlogsBackend.closeConnection(rabbitMQ)
