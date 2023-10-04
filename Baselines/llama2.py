import openai
import os
import re
import time
import string
from tqdm import tqdm

# For easily reproducation

openai.api_key = ""
openai.api_base = "https://api.deepinfra.com/v1/openai"


def infer_llm(instruction, query, model='meta-llama/Llama-2-70b-chat-hf',temperature=0.0):
    messages = [{"role": "user", "content": instruction+"```\n"+query+"```\n"},
        ]
    retry_times = 0
    if "llama" in model:
        while retry_times < 3:
            try:
                answers = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    stream=False,
                    temperature=temperature
                )
                return [response["message"]["content"] for response in answers["choices"] if response['finish_reason'] != 'length'][0]

                # return [response["message"]["content"] for response in answers["choices"] if response['finish_reason'] != 'length'][0]
            except Exception as e:
                print("Exception :", e)
                if "list index out of range" in str(e):
                    break
                # print(answers)
                retry_times += 1


def get_instruction():

    instruction = \
    """
    You have been given a Java method code which lacks of one logging statement. Your task is to insert one and only one logging statement starts with "log.". Make sure not to modify any other code or import any package, don't reply me any other code.

    response_format:
    <Line number>:
    <Logging statement>:

    Example 1:
    <Java code>:
    /**
 * Calls {@link AccumuloInputFormat#setConnectorInfo(JobConf, String, AuthenticationToken)},
 * suppressing exceptions due to setting the configuration multiple times.
 */
public void setInputFormatConnectorInfo(JobConf conf, String username, AuthenticationToken token) throws AccumuloSecurityException {
    try {
        AccumuloInputFormat.setConnectorInfo(conf, username, token);
    } catch (IllegalStateException e) {
        // AccumuloInputFormat complains if you re-set an already set value. We just don't care.
            throw e;
            }
}

   <Output>:
   <Line number>: 10
   <Logging statement>: log.debug("Ignoring exception setting Accumulo Connector instance for user " + username, e);
   
    Example 2:

   <Java code>:
   /**
 * Prints a summary of important details about the chore. Used for debugging purposes
 */
private void printChoreDetails(final String header, ScheduledChore chore) {
    LinkedHashMap<String, String> output = new LinkedHashMap<>();
    output.put(header, "");
    output.put("Chore period: ", Integer.toString(chore.getPeriod()));
    output.put("Chore timeBetweenRuns: ", Long.toString(chore.getTimeBetweenRuns()));
    for (Entry<String, String> entry : output.entrySet()) {
        output.put("Chore name: ", chore.getName());
}

   <Output>:
   <Line number>: 12
   <Logging statement>:  LOG.trace(entry.getKey() + entry.getValue());


    The following is the java code needs to be inserted:
    <Java code>:
    """

    return instruction



def main():
    input_folder = "../ExperimentResults/test"
    output_folder = "../ExperimentResults/llama2"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in tqdm(os.listdir(input_folder)):
        if filename.endswith(".java"):
            with open(os.path.join(input_folder, filename), "r") as f:
                file_contents = f.read()
            
            # process file contents with infer_llm function
            processed_contents = infer_llm(get_instruction(), file_contents)

            # write processed contents to output file
            with open(os.path.join(output_folder, filename), "w") as f:
                try:
                    f.write(processed_contents)
                except:
                    pass


if __name__ == "__main__":
    main()