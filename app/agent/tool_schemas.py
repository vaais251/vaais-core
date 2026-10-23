LOOKUP_OFFERING_SCHEMA={
  "type": "function",
  "name": "lookup_offering",
  "description": "Retrieves synthetic offers from the local catalog.",
  "parameters": {
    "type": "object",
    "properties": {
      "offering_id": {
        "type": "string",
        "description": "The ID of the synthetic offer to retrieve."
      }
    },
    "required": [
      "offering_id"
    ],
    "additionalProperties": False
  }
}
