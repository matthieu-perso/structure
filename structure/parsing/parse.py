import json, os, traceback
import itertools
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import RetryWithErrorOutputParser
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser, RetryOutputParser
from collections import defaultdict, Counter
from typing import Dict
import asyncio
from parsing.utils.json_fixer import fix_json
from models.get_classes import get_data_classes_for_fields
from parsing.file_handlers import generate_chunks
from models.models import ResumeSchema
import logging

logging.basicConfig(level=logging.INFO)

API_KEY = os.environ['OPENAI_API_KEY']

llm = OpenAI(model_name="gpt-3.5-turbo", max_tokens=-1,  temperature=0, openai_api_key=API_KEY)


class LLMParser:
    def __init__(self, pydantic_def, cv_chunk:str) -> None:
        self.parsing_rule = pydantic_def
        self.cv_chunk = cv_chunk
        self.pydantic_def()

    
    def pydantic_def(self):
        self.parser = PydanticOutputParser(pydantic_object=self.parsing_rule)
        self.prompt = PromptTemplate(
            template="Parse the data according to instructions.\n{format_instructions}\n. Data : {unstructured_data}\n",
            input_variables=["unstructured_data"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )


    async def parse(self, data_chunk:str) -> Dict:

        _input = self.prompt.format_prompt(unstructured_data=data_chunk)

        ''' Async'''
        output = await llm.agenerate([_input.to_string()])
        print("Output", output)
        return output.generations[0][0].text

        """ Synchronous
        output = llm(_input.to_string())
        print("Output", output)
        parsed_output = None
        return output
        """

        """
    
        print("Running")
        output = await llm.agenerate(_input.to_string())
        #output = output.generations[0][0].text

        print("Output", output)
        parsed_output = None
        return output
    
        
        WIP 

        try: 
            parsed_output = self.parser.parse(output)
            print("Parsed", parsed_output)
            return parsed_output.dict()
        except Exception as e: 
            fixed_output = None
            try:
                fixed_output =  LLMFixer().fix(parsed_output, self.parser)
                print("Fixed", fixed_output)
                return fixed_output.dict()
            except:
                try:
                    retried_output =  LLMFixer().retry(fixed_output, self.parser, self.prompt)
                    return retried_output.dict()
                except Exception as e: 
                    print(e)
        """
        
        
class LLMFixer:

    def fix(self, output, parser):
        fix_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)
        fixed_output =  fix_parser.parse(output)
        return fixed_output


    def retry(self, output, parser, prompt_value:PromptTemplate):
        retry_parser = RetryWithErrorOutputParser.from_llm(parser=parser, llm=llm)
        retried_output = retry_parser.parse_with_prompt(output, prompt_value)
        return retried_output


# Run script / For recap of the methodology, see the README.md file in the root of the repository.


async def parse_data(file):
    schema_chunks = get_data_classes_for_fields(ResumeSchema)
    cv_chunks = generate_chunks(file)

    # Get the Cartesian product of the two lists
    parsing_combination = list(itertools.product(list(schema_chunks.values()), cv_chunks))

    async def parse_schema_cv_chunk(schema, cv_chunk):
        print("Loading schema: ", schema), 
        
        llm_parser = LLMParser(pydantic_def=schema, cv_chunk=cv_chunk)
        llm_parser.pydantic_def()
        parsed_result = await llm_parser.parse(cv_chunk=cv_chunk)
        
        print(f"Parsed Result for {schema}: ", parsed_result, "Type:", type(parsed_result))
        
        try:
            parsed_result = json.loads(parsed_result)
        except json.decoder.JSONDecodeError:
            print("JSONDecodeError. Fixing...")
            logging.info("JSONDecodeError. Fixing...")
            try:
                parsed_result = fix_json(parsed_result)
                print("Fixed JSON...")
            except json.decoder.JSONDecodeError:
                print("Failed to fix JSONDecodeError.")
                pass
        except Exception as e: 
            print(f"Unhandled Exception: {traceback.format_exc()}")
            pass

        if parsed_result:
            return {"schema": str(schema).split(".")[-1][:-2], "results": parsed_result}
        return None

    # Prepare the list of coroutines
    coros = [parse_schema_cv_chunk(schema, cv_chunk) for schema, cv_chunk in parsing_combination]

    # Gather and run all coroutines
    parsed_results = await asyncio.gather(*coros)
    
    # Filter out None values
    parsed_results = list(filter(None, parsed_results))

    # write results in json file 
    return parsed_results
