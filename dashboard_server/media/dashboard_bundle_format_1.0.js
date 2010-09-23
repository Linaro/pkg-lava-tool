{
	"description": "DashboadBundle object",
	"type": "object",
	"additionalProperties": false,
	"properties": {
		"format": {
			"description": "Document format identifier. Currently hardcoded to the only existing format",
			"type": "string",
			"enum": ["Dashboard Bundle Format 1.0"]
		},
		"test_runs": {
			"description": "Array of TestRun objects",
			"type": "array",
			"optional": true,
			"items": {
				"description": "TestRun object",
				"type": "object",
				"additionalProperties": false,
				"properties": {
					"analyzer_assigned_uuid": {
						"description": "UUID that was assigned by the log analyzer during processing",
						"type": "string"
					},
					"analyzer_assigned_date": {
						"description": "Time stamp in ISO 8601 format that was assigned by the log analyzer during processing. The exact format is YYYY-MM-DDThh:mm:ssZ",
						"type": "string",
						"format": "date-time"
					},
					"time_check_performed": {
						"description": "Indicator on whether the log analyzer had accurate time information",
						"type": "boolean"
					},
					"attributes": {
						"description": "Container for additional attributes defined by the test and their values during this particular run",
						"type": "object",
						"optional": true,
						"additionalProperties": {
							"description": "Arbitrary properties that are defined by the test",
							"type": "string"
						}
					},
					"test_id": {
						"description": "Test identifier. Must be a well-defined (in scope of the dashboard) name of the test",
						"type": "string"
					},
					"test_results": {
						"description": "Array of TestResult objects",
						"type": "array",
						"items": {
							"description": "TestResult object",
							"type": "object",
							"additionalProperties": false,
							"properties": {
								"test_case_id": {
									"description": "Identifier of the TestCase this test result came from",
									"type": "string",
									"optional": true
								},
								"result": {
									"description": "Status code of this test result",
									"type": "string",
									"enum": ["pass", "fail", "skip", "unknown"]
								},
								"message": {
									"description": "Message scrubbed from the log file",
									"type": "string",
									"optional": true
								},
								"measurement": {
									"description": "Numerical measurement associated with the test result",
									"type": "number",
									"optional": true,
									"requires": "test_case_id"
								},
								"units": {
									"description": "Units for measurement",
									"type": "string",
									"optional": true,
									"requires": "measurement"
								},
								"timestamp": {
									"description": "Date and time when the test was performed",
									"type": "string",
									"optional": true,
									"format": "date-time"
								},
								"duration": {
									"description": "Duration of the test case. Duration is stored in the following format '[DAYS]d [SECONDS]s [MICROSECONDS]us'",
									"type": "string",
									"optional": true
								},
								"log_filename": {
									"description": "Filename of the log file which this test result was scrubbed from",
									"type": "string",
									"optional": true
								},
								"log_lineno": {
									"description": "Precise location in the log file (line number)",
									"type": "integer",
									"optional": true,
									"requires": "log_filename"
								},
								"attributes": {
									"description": "Container for additional attributes defined by test result",
									"type": "object",
									"optional": true,
									"additionalProperties": {
										"description": "Arbitrary properties that are defined by the particular test result",
										"type": "string"
									}
								}
							}
						}
					},
					"attachments": {
						"description": "Object with text attachments",
						"type": "object",
						"additionalProperties": {
							"description": "Attachments represented as file name (property) and array of text liens (value)",
							"type": "array",
							"items": {
								"type": "string"
							}
						}
					},
					"hardware_context": {
						"description": "Description of the hardware context in which this test was running",
						"type": "object",
						"additionalProperties": false,
						"properties": {
							"devices": {
								"description": "Array of HardwareDevice objects",
								"type": "array",
								"items": {
									"description": "HardwareDevice object",
									"type": "object",
									"properties": {
										"type": "string",
										"description": "Device type"
									},
									"attributes": {
										"description": "Container for additional attributes defined by the device",
										"type": "object",
										"optional": true,
										"additionalProperties": {
											"description": "Arbitrary properties that are defined by the particular hardware device",
											"type": "string"
										}
									}
								}
							}
						}
					},
					"software_context": {
						"description": "Description of the software context in which this test was running",
						"type": "object",
						"additionalProperties": false,
						"properties": {
							"sw_image": {
								"description": "SoftwareImage object",
								"type": "object",
								"additionalProperties": false,
								"properties": {
									"desc": {
										"description": "Description of the operating system image",
										"type": "string"
									}
								}
							},
							"packages": {
								"description": "Array of SoftwarePackage objects",
								"type": "array",
								"items": {
									"description": "SoftwarePackage object",
									"type": "object",
									"additionalProperties": false,
									"properties": {
										"name": {
											"description": "Package name",
											"type": "string"
										},
										"version": {
											"description": "Package version",
											"type": "string"
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}
}
