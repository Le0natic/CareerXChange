import OpenAI from "openai";
import dotenv from "dotenv";

dotenv.config({ path: "../.env" });

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function main() {
  const response = await client.responses.create({
    model: "gpt-4.1-mini",
    input: "Explain event-driven architecture in one paragraph."
  });

  console.log(response.output[0].content[0].text);
}

main();