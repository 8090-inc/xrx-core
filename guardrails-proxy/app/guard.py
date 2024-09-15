from guardrails import Guard, OnFailAction
from guardrails.hub import ToxicLanguage
from dotenv import load_dotenv
import logging
import json
import time

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

guard = Guard().use_many(
    ToxicLanguage(threshold=0.5, use_local=True, validation_method="sentence", on_fail=OnFailAction.EXCEPTION))

def validate_text(text):
    start_time = time.time()
    result = {
        "validation_passed": None,
        "validated_output": None
    }
    
    try:
        validation_result = guard.validate(text)
        result["validation_passed"] = True
        result["validated_output"] = validation_result.validated_output
    except Exception as e:
        logging.error(f"Validation failed: {e}")
        result["validation_passed"] = False
        result["validated_output"] = str(e)
    elapsed_time = time.time() - start_time
    logging.info(f"Guardrails result: {result}, validation time: {elapsed_time} seconds")
    return json.dumps(result)