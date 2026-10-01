from pathlib import Path
import yaml

def generate_dev_scenarios():
    scenarios = [
        {
            "scenario_id": "dev_01",
            "title": "Family plan phone reuse",
            "ambiguity_type": "reused_phone",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Mark Miller",
                    "canonical_email": "mark.miller@gmail.com",
                    "canonical_phone": "+15550100"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Sarah Miller",
                    "canonical_email": "sarah.m@gmail.com",
                    "canonical_phone": "+15550100"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T10:00:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+15550100",
                    "display_name": None,
                    "text": "Hi, I would like to check status on order 8821. Thanks, Mark Miller, mark.miller@gmail.com.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T10:15:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+15550100",
                    "display_name": None,
                    "text": "Hello, this is Sarah Miller calling from our family line about my dental package receipt. Email sarah.m@gmail.com.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T10:30:00Z",
                    "channel": "email",
                    "sender_email": "mark.miller@gmail.com",
                    "sender_phone": None,
                    "display_name": "Mark Miller",
                    "text": "Checking in on order 8821. Can you email receipt to mark.miller@gmail.com?",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-01T11:00:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+15550100",
                    "display_name": None,
                    "text": "Please confirm delivery time for Sarah dental package. Sarah Miller.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "dev_02",
            "title": "Corporate domain overlap",
            "ambiguity_type": "shared_domain",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Alice Vance",
                    "canonical_email": "alice.vance@acme-logistics.com",
                    "canonical_phone": "+14155550201"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Bob Vance",
                    "canonical_email": "bob.vance@acme-logistics.com",
                    "canonical_phone": "+14155550202"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T09:00:00Z",
                    "channel": "email",
                    "sender_email": "alice.vance@acme-logistics.com",
                    "sender_phone": None,
                    "display_name": "Alice Vance",
                    "text": "Inquiring about enterprise fleet pricing for Q4 logistics. Reach my desk at +14155550201.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T09:30:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+14155550201",
                    "display_name": None,
                    "text": "Hi, Alice Vance from Acme here regarding the Q4 fleet proposal.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T10:00:00Z",
                    "channel": "email",
                    "sender_email": "bob.vance@acme-logistics.com",
                    "sender_phone": None,
                    "display_name": "Bob Vance",
                    "text": "Need login access to warehouse management dashboard. Phone +14155550202.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-01T10:20:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+14155550202",
                    "display_name": None,
                    "text": "This is Bob Vance from Acme calling to verify warehouse credentials.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "dev_03",
            "title": "Anonymous voice clinic check",
            "ambiguity_type": "name_only",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Johnathan Doe",
                    "canonical_email": "j.doe92@outlook.com",
                    "canonical_phone": "+16175550301"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "John Doe",
                    "canonical_email": "john.doe.md@hospital.org",
                    "canonical_phone": "+16175550399"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T08:00:00Z",
                    "channel": "email",
                    "sender_email": "j.doe92@outlook.com",
                    "display_name": "Johnathan Doe",
                    "sender_phone": None,
                    "text": "Need prescription refill for Lipitor medication. Phone +16175550301.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T08:15:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+16175550301",
                    "display_name": None,
                    "text": "This is Johnathan Doe, checking if refill is approved.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T09:00:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": None,
                    "display_name": None,
                    "text": "Hello, this is John Doe calling to inquire about pediatric clinic open hours tomorrow.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-01T09:30:00Z",
                    "channel": "email",
                    "sender_email": "john.doe.md@hospital.org",
                    "display_name": "John Doe",
                    "sender_phone": None,
                    "text": "Checking on pediatric facility availability schedule. Office +16175550399.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "dev_04",
            "title": "Clean cross channel warranty flow",
            "ambiguity_type": "none",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Elena Rostova",
                    "canonical_email": "elena.rostova@techcorp.com",
                    "canonical_phone": "+12065550401"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T12:00:00Z",
                    "channel": "email",
                    "sender_email": "elena.rostova@techcorp.com",
                    "sender_phone": None,
                    "display_name": "Elena Rostova",
                    "text": "I submitted warranty replacement request W991 for broken display. You can reach my mobile at +12065550401.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T12:20:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+12065550401",
                    "display_name": None,
                    "text": "Hi, Elena Rostova here. Can I drop off the defective device in Seattle?",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T12:45:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+12065550401",
                    "display_name": None,
                    "text": "Calling to confirm Seattle drop-off address for warranty W991, Elena Rostova at elena.rostova@techcorp.com.",
                    "true_identity_id": "user_1"
                }
            ]
        },
        {
            "scenario_id": "dev_05",
            "title": "Recycled VOIP tenant conflict",
            "ambiguity_type": "reused_phone",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Marcus Vance",
                    "canonical_email": "marcus.v@protonmail.com",
                    "canonical_phone": "+13125550500"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Chloe Higgins",
                    "canonical_email": "chloe.higgins@gmail.com",
                    "canonical_phone": "+13125550500"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-09-01T10:00:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+13125550500",
                    "display_name": None,
                    "text": "Marcus Vance here, checking if my apartment security deposit was mailed to marcus.v@protonmail.com.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-09-01T10:15:00Z",
                    "channel": "email",
                    "sender_email": "marcus.v@protonmail.com",
                    "sender_phone": None,
                    "display_name": "Marcus Vance",
                    "text": "Following up on lease refund deposit for Marcus Vance.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T11:00:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+13125550500",
                    "display_name": None,
                    "text": "Hi this is Chloe Higgins, I just got this new number and I want to set up internet service. Email is chloe.higgins@gmail.com.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-01T11:15:00Z",
                    "channel": "email",
                    "sender_email": "chloe.higgins@gmail.com",
                    "sender_phone": None,
                    "display_name": "Chloe Higgins",
                    "text": "Internet setup request for apartment 4B, Chloe Higgins.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "dev_06",
            "title": "University academic department overlap",
            "ambiguity_type": "shared_domain",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Charles Davis",
                    "canonical_email": "c.davis@state.edu",
                    "canonical_phone": "+15125550601"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Maria Martinez",
                    "canonical_email": "m.martinez@state.edu",
                    "canonical_phone": "+15125550602"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T14:00:00Z",
                    "channel": "email",
                    "sender_email": "c.davis@state.edu",
                    "sender_phone": None,
                    "display_name": "Charles Davis",
                    "text": "NSF grant application review for biology department lab equipment. Cell +15125550601.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T14:10:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+15125550601",
                    "display_name": None,
                    "text": "Charles Davis here following up on the NSF grant submission.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T14:30:00Z",
                    "channel": "email",
                    "sender_email": "m.martinez@state.edu",
                    "sender_phone": None,
                    "display_name": "Maria Martinez",
                    "text": "Budget approvals for engineering faculty travel expenses. Phone +15125550602.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-01T14:40:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+15125550602",
                    "display_name": None,
                    "text": "Maria Martinez calling about engineering department fiscal year budget.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "dev_07",
            "title": "Hotel lobby speakerphone checkin",
            "ambiguity_type": "name_only",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Michael Chang",
                    "canonical_email": "michael.chang@apex.com",
                    "canonical_phone": "+14085550701"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T15:00:00Z",
                    "channel": "email",
                    "sender_email": "michael.chang@apex.com",
                    "sender_phone": None,
                    "display_name": "Michael Chang",
                    "text": "Booking conference room B for tomorrow afternoon board meeting. Contact +14085550701.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T15:15:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+14085550701",
                    "display_name": None,
                    "text": "Michael Chang here, need four extra chairs for conference room B.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T15:45:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": None,
                    "display_name": None,
                    "text": "Hi this is Michael Chang calling from reception desk phone. Could you bring HDMI adapters to room B?",
                    "true_identity_id": "user_1"
                }
            ]
        },
        {
            "scenario_id": "dev_08",
            "title": "Clean solar equipment order",
            "ambiguity_type": "none",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "James Wright",
                    "canonical_email": "j.wright@gmail.com",
                    "canonical_phone": "+13035550801"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T11:00:00Z",
                    "channel": "email",
                    "sender_email": "j.wright@gmail.com",
                    "sender_phone": None,
                    "display_name": "James Wright",
                    "text": "Order confirmation for solar battery SB4401 shipment. You can text status updates to +13035550801.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T11:20:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+13035550801",
                    "display_name": None,
                    "text": "James Wright: is expedited shipping available for battery SB4401?",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T11:40:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+13035550801",
                    "display_name": None,
                    "text": "James Wright calling to confirm solar battery dispatch date for j.wright@gmail.com.",
                    "true_identity_id": "user_1"
                }
            ]
        },
        {
            "scenario_id": "dev_09",
            "title": "Trucking dispatcher shared line",
            "ambiguity_type": "reused_phone",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Karen Miller",
                    "canonical_email": "karen.dispatch@logisticsgroup.com",
                    "canonical_phone": "+14045550900"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Tom Hayes",
                    "canonical_email": "tom.driver@logisticsgroup.com",
                    "canonical_phone": "+14045550900"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T07:00:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+14045550900",
                    "display_name": None,
                    "text": "Dispatcher Karen Miller here, scheduling maintenance for rig 12. Email karen.dispatch@logisticsgroup.com.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T07:15:00Z",
                    "channel": "email",
                    "sender_email": "karen.dispatch@logisticsgroup.com",
                    "sender_phone": None,
                    "display_name": "Karen Miller",
                    "text": "Rig 12 maintenance paperwork attached for billing. Karen Miller.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T08:00:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+14045550900",
                    "display_name": None,
                    "text": "Driver Tom Hayes here, Rig 12 has flat tire on highway 85. Email tom.driver@logisticsgroup.com.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-01T08:30:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+14045550900",
                    "display_name": None,
                    "text": "Tom Hayes again, roadside tow assistance is on site at mile marker 40.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "dev_10",
            "title": "Startup founders domain overlap",
            "ambiguity_type": "shared_domain",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Rachel Green",
                    "canonical_email": "ceo@nexus.io",
                    "canonical_phone": "+16505551001"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Devon Patel",
                    "canonical_email": "cto@nexus.io",
                    "canonical_phone": "+16505551002"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T16:00:00Z",
                    "channel": "email",
                    "sender_email": "ceo@nexus.io",
                    "sender_phone": None,
                    "display_name": "Rachel Green",
                    "text": "Reviewing cloud vendor billing contracts and legal retainer invoices. Direct line +16505551001.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T16:20:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+16505551001",
                    "display_name": None,
                    "text": "Rachel Green from Nexus, sending over signed legal retainer.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T16:40:00Z",
                    "channel": "email",
                    "sender_email": "cto@nexus.io",
                    "sender_phone": None,
                    "display_name": "Devon Patel",
                    "text": "Kubernetes cluster security audit results and vulnerability logs. Direct line +16505551002.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-01T17:00:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+16505551002",
                    "display_name": None,
                    "text": "Devon Patel here, urgent server vulnerability patch needed on worker nodes.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "dev_11",
            "title": "Marketing voice transcript follow up",
            "ambiguity_type": "name_only",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Sarah Connor",
                    "canonical_email": "sarah.connor@cyber.org",
                    "canonical_phone": "+17025551101"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T13:00:00Z",
                    "channel": "email",
                    "sender_email": "sarah.connor@cyber.org",
                    "sender_phone": None,
                    "display_name": "Sarah Connor",
                    "text": "Q3 product marketing campaign review for upcoming product rollout. Cell +17025551101.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T13:20:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+17025551101",
                    "display_name": None,
                    "text": "Sarah Connor: campaign draft uploaded to shared folder.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T13:50:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": None,
                    "display_name": None,
                    "text": "Hey this is Sarah Connor from marketing, just checking if you saw my email about the Q3 campaign.",
                    "true_identity_id": "user_1"
                }
            ]
        },
        {
            "scenario_id": "dev_12",
            "title": "Airline flight seat change",
            "ambiguity_type": "none",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Liam Becker",
                    "canonical_email": "liam.becker@berlin-tech.de",
                    "canonical_phone": "+12125551201"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T06:00:00Z",
                    "channel": "email",
                    "sender_email": "liam.becker@berlin-tech.de",
                    "sender_phone": None,
                    "display_name": "Liam Becker",
                    "text": "Requesting seat change on flight LH404 to aisle seat. SMS contact +12125551201.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T06:20:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+12125551201",
                    "display_name": None,
                    "text": "Liam Becker here, confirming aisle seat request for flight LH404.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T06:40:00Z",
                    "channel": "email",
                    "sender_email": "liam.becker@berlin-tech.de",
                    "sender_phone": None,
                    "display_name": "Liam Becker",
                    "text": "Can I also add an extra checked bag to flight LH404? Liam Becker, +12125551201.",
                    "true_identity_id": "user_1"
                }
            ]
        },
        {
            "scenario_id": "dev_13",
            "title": "Parent and teenager clinic billing",
            "ambiguity_type": "reused_phone",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Laura Hernandez",
                    "canonical_email": "laura.h@miami.edu",
                    "canonical_phone": "+13055551300"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Kevin Hernandez",
                    "canonical_email": "kevin.h@miami.edu",
                    "canonical_phone": "+13055551300"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T11:00:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+13055551300",
                    "display_name": None,
                    "text": "Hi this is Laura Hernandez, need to pay dental copay for Kevin. Email laura.h@miami.edu.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T11:20:00Z",
                    "channel": "email",
                    "sender_email": "laura.h@miami.edu",
                    "sender_phone": None,
                    "display_name": "Laura Hernandez",
                    "text": "Receipt needed for Kevin dental cleaning insurance claim. Laura Hernandez.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T14:00:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+13055551300",
                    "display_name": None,
                    "text": "Hey it is Kevin Hernandez, can I move my orthodontic bracket appointment? Email kevin.h@miami.edu.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-01T14:30:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+13055551300",
                    "display_name": None,
                    "text": "Kevin Hernandez calling, checking if 4pm Tuesday works for braces adjustment.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "dev_14",
            "title": "Hospital staff cross department emails",
            "ambiguity_type": "shared_domain",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Emily Watson",
                    "canonical_email": "e.watson@metrohealth.org",
                    "canonical_phone": "+13125551401"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Robert Chen",
                    "canonical_email": "r.chen@metrohealth.org",
                    "canonical_phone": "+13125551402"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T08:00:00Z",
                    "channel": "email",
                    "sender_email": "e.watson@metrohealth.org",
                    "sender_phone": None,
                    "display_name": "Emily Watson",
                    "text": "Cardiology lab schedule for Friday catheterization clinic. Pager +13125551401.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T08:15:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+13125551401",
                    "display_name": None,
                    "text": "Dr Watson: lab specimens dispatched to cardiology pathology.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T09:00:00Z",
                    "channel": "email",
                    "sender_email": "r.chen@metrohealth.org",
                    "sender_phone": None,
                    "display_name": "Robert Chen",
                    "text": "ICU telemetry bed census update for surgical wards. Pager +13125551402.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-01T09:30:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+13125551402",
                    "display_name": None,
                    "text": "Nurse Robert Chen calling with telemetry ICU bed requests for neurology.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "dev_15",
            "title": "Conference registration walk in",
            "ambiguity_type": "name_only",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "David Ross",
                    "canonical_email": "david.ross@summit.org",
                    "canonical_phone": "+16195551501"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T07:30:00Z",
                    "channel": "email",
                    "sender_email": "david.ross@summit.org",
                    "sender_phone": None,
                    "display_name": "David Ross",
                    "text": "Badge registration for AI developer summit keynote access. Cell +16195551501.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T08:00:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": None,
                    "display_name": None,
                    "text": "This is David Ross, checking if keynote badge is ready at will call counter.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T08:20:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+16195551501",
                    "display_name": None,
                    "text": "David Ross here at check-in counter A regarding developer badge.",
                    "true_identity_id": "user_1"
                }
            ]
        },
        {
            "scenario_id": "dev_16",
            "title": "Fraudulent banking dispute resolution",
            "ambiguity_type": "none",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Priya Patel",
                    "canonical_email": "priya.patel@sfbay.org",
                    "canonical_phone": "+14155551601"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T17:00:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+14155551601",
                    "display_name": None,
                    "text": "Priya Patel calling to dispute fraudulent charge of 450 dollars. Account email is priya.patel@sfbay.org.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T17:10:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+14155551601",
                    "display_name": None,
                    "text": "Priya Patel: confirming fraud freeze on debit card ending 1092.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T17:30:00Z",
                    "channel": "email",
                    "sender_email": "priya.patel@sfbay.org",
                    "sender_phone": None,
                    "display_name": "Priya Patel",
                    "text": "Signed fraud dispute affidavit attached for debit card 1092. Contact +14155551601.",
                    "true_identity_id": "user_1"
                }
            ]
        },
        {
            "scenario_id": "dev_17",
            "title": "Meeting room speakerphone repairs",
            "ambiguity_type": "reused_phone",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Dave Miller",
                    "canonical_email": "dave.m@enterprise.com",
                    "canonical_phone": "+18005551700"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Jessica Alba",
                    "canonical_email": "jessica.a@enterprise.com",
                    "canonical_phone": "+18005551700"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T10:00:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+18005551700",
                    "display_name": None,
                    "text": "Dave Miller here from conference room A, audio speaker is buzzing. Ticket to dave.m@enterprise.com.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T10:15:00Z",
                    "channel": "email",
                    "sender_email": "dave.m@enterprise.com",
                    "sender_phone": None,
                    "display_name": "Dave Miller",
                    "text": "Audio ticket for Conf Room A speaker buzzing issue. Dave Miller.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T11:00:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+18005551700",
                    "display_name": None,
                    "text": "Jessica Alba from conference room A, video projector will not turn on. Email jessica.a@enterprise.com.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-01T11:20:00Z",
                    "channel": "email",
                    "sender_email": "jessica.a@enterprise.com",
                    "sender_phone": None,
                    "display_name": "Jessica Alba",
                    "text": "Projector HDMI cable replacement needed in Room A. Jessica Alba.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "dev_18",
            "title": "Corporate accounting aliases",
            "ambiguity_type": "shared_domain",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Vertex Billing",
                    "canonical_email": "billing@vertex.com",
                    "canonical_phone": "+16175551801"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Vertex Tax Team",
                    "canonical_email": "tax@vertex.com",
                    "canonical_phone": "+16175551802"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T09:00:00Z",
                    "channel": "email",
                    "sender_email": "billing@vertex.com",
                    "sender_phone": None,
                    "display_name": "Vertex Billing",
                    "text": "Invoice 9012 for software licensing renewal is overdue. Contact +16175551801.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T09:20:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+16175551801",
                    "display_name": None,
                    "text": "Vertex accounts receivable: payment received for invoice 9012.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T10:00:00Z",
                    "channel": "email",
                    "sender_email": "tax@vertex.com",
                    "sender_phone": None,
                    "display_name": "Vertex Tax Team",
                    "text": "W9 tax exemption form requested for vendor onboarding. Contact +16175551802.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-01T10:30:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+16175551802",
                    "display_name": None,
                    "text": "Vertex tax compliance department calling regarding 1099 form verification.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "dev_19",
            "title": "Auto repair estimate voicemail",
            "ambiguity_type": "name_only",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Alex Petrov",
                    "canonical_email": "alex.petrov@speedmotors.com",
                    "canonical_phone": "+12065551901"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T14:00:00Z",
                    "channel": "email",
                    "sender_email": "alex.petrov@speedmotors.com",
                    "sender_phone": None,
                    "display_name": "Alex Petrov",
                    "text": "Quote 401 for transmission repair on Honda Civic sedan. Mobile +12065551901.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T14:20:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+12065551901",
                    "display_name": None,
                    "text": "Alex Petrov: replacement transmission parts will arrive by Wednesday.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T15:00:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": None,
                    "display_name": None,
                    "text": "Hi this is Alex Petrov following up on the Civic transmission replacement estimate.",
                    "true_identity_id": "user_1"
                }
            ]
        },
        {
            "scenario_id": "dev_20",
            "title": "Subscription cancellation flow",
            "ambiguity_type": "none",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Maya Lin",
                    "canonical_email": "maya.lin@designer.co",
                    "canonical_phone": "+15035552001"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-01T11:00:00Z",
                    "channel": "email",
                    "sender_email": "maya.lin@designer.co",
                    "sender_phone": None,
                    "display_name": "Maya Lin",
                    "text": "Requesting cancellation of Pro plan annual subscription. You can send confirmation SMS to +15035552001.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-01T11:10:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+15035552001",
                    "display_name": None,
                    "text": "Maya Lin: 2FA security code 489211 to confirm account cancellation.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-01T11:30:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+15035552001",
                    "display_name": None,
                    "text": "Maya Lin here at maya.lin@designer.co, just verifying subscription cancellation was processed.",
                    "true_identity_id": "user_1"
                }
            ]
        }
    ]

    dev_dir = Path("data/dev")
    dev_dir.mkdir(parents=True, exist_ok=True)
    for s in scenarios:
        path = dev_dir / f"{s['scenario_id']}.yaml"
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(s, f, sort_keys=False)

def generate_test_scenarios():
    scenarios = [
        {
            "scenario_id": "test_01",
            "title": "Elderly patient and caregiver landline",
            "ambiguity_type": "reused_phone",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Frank Evans",
                    "canonical_email": "frank.evans88@gmail.com",
                    "canonical_phone": "+18185553001"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Nancy Cole",
                    "canonical_email": "nancy.caregiver@agency.org",
                    "canonical_phone": "+18185553001"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-02T08:00:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+18185553001",
                    "display_name": None,
                    "text": "Frank Evans here, need walker delivery confirmation for frank.evans88@gmail.com.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-02T08:15:00Z",
                    "channel": "email",
                    "sender_email": "frank.evans88@gmail.com",
                    "sender_phone": None,
                    "display_name": "Frank Evans",
                    "text": "Medical equipment prescription for walker attached. Reach me at +18185553001.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-02T09:00:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+18185553001",
                    "display_name": None,
                    "text": "Hello this is Nancy Cole, caregiver for Frank Evans, calling about medication delivery. Email nancy.caregiver@agency.org.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-02T09:20:00Z",
                    "channel": "email",
                    "sender_email": "nancy.caregiver@agency.org",
                    "sender_phone": None,
                    "display_name": "Nancy Cole",
                    "text": "Caregiver authorization form for Frank Evans medical records. Nancy Cole.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "test_02",
            "title": "Law firm partner domain overlap",
            "ambiguity_type": "shared_domain",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Henry Adams",
                    "canonical_email": "henry.adams@lexlegal.com",
                    "canonical_phone": "+12125553201"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Clara Oswald",
                    "canonical_email": "clara.oswald@lexlegal.com",
                    "canonical_phone": "+12125553202"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-02T10:00:00Z",
                    "channel": "email",
                    "sender_email": "henry.adams@lexlegal.com",
                    "sender_phone": None,
                    "display_name": "Henry Adams",
                    "text": "Deposition schedule for antitrust litigation case 774. Cell +12125553201.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-02T10:15:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+12125553201",
                    "display_name": None,
                    "text": "Henry Adams: deposition transcripts uploaded to document vault.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-02T11:00:00Z",
                    "channel": "email",
                    "sender_email": "clara.oswald@lexlegal.com",
                    "sender_phone": None,
                    "display_name": "Clara Oswald",
                    "text": "Patent licensing agreement draft for robotics client. Mobile +12125553202.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-02T11:20:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+12125553202",
                    "display_name": None,
                    "text": "Clara Oswald calling to verify patent filing deadline with USPTO.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "test_03",
            "title": "Guitar repair shop walk in voicemail",
            "ambiguity_type": "name_only",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "George Harrison",
                    "canonical_email": "george.h@vintageguitars.com",
                    "canonical_phone": "+16155553301"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-02T13:00:00Z",
                    "channel": "email",
                    "sender_email": "george.h@vintageguitars.com",
                    "sender_phone": None,
                    "display_name": "George Harrison",
                    "text": "Inquiry regarding fret leveling on 1968 Stratocaster neck. Reach me at +16155553301.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-02T13:20:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+16155553301",
                    "display_name": None,
                    "text": "George Harrison: dropped off the guitar at front desk this morning.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-02T14:00:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": None,
                    "display_name": None,
                    "text": "Hi this is George Harrison checking if the Stratocaster truss rod was adjusted.",
                    "true_identity_id": "user_1"
                }
            ]
        },
        {
            "scenario_id": "test_04",
            "title": "Clean apparel customer exchange",
            "ambiguity_type": "none",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Samantha Brooks",
                    "canonical_email": "samantha.brooks@gmail.com",
                    "canonical_phone": "+12065553401"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-02T09:00:00Z",
                    "channel": "email",
                    "sender_email": "samantha.brooks@gmail.com",
                    "sender_phone": None,
                    "display_name": "Samantha Brooks",
                    "text": "Exchange request for winter wool parka from medium to large. You can reach my mobile at +12065553401.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-02T09:20:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+12065553401",
                    "display_name": None,
                    "text": "Samantha Brooks: return label generated for parka exchange.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-02T09:40:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+12065553401",
                    "display_name": None,
                    "text": "Samantha Brooks calling to verify the replacement parka for samantha.brooks@gmail.com has shipped.",
                    "true_identity_id": "user_1"
                }
            ]
        },
        {
            "scenario_id": "test_05",
            "title": "Pizzeria kitchen and driver shared phone",
            "ambiguity_type": "reused_phone",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Marco Rossi",
                    "canonical_email": "chef.marco@ristorante.com",
                    "canonical_phone": "+13125553500"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Leo Bianchi",
                    "canonical_email": "leo.driver@ristorante.com",
                    "canonical_phone": "+13125553500"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-02T16:00:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+13125553500",
                    "display_name": None,
                    "text": "Chef Marco Rossi calling, need bulk organic flour delivery. Email chef.marco@ristorante.com.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-02T16:20:00Z",
                    "channel": "email",
                    "sender_email": "chef.marco@ristorante.com",
                    "sender_phone": None,
                    "display_name": "Marco Rossi",
                    "text": "Purchase order PO-991 for organic pizza flour and olive oil. Marco Rossi.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-02T18:00:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+13125553500",
                    "display_name": None,
                    "text": "Delivery driver Leo Bianchi here, scooter headlight is broken. Email leo.driver@ristorante.com.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-02T18:20:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+13125553500",
                    "display_name": None,
                    "text": "Leo Bianchi calling again, taking backup vehicle for orders in West Loop.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "test_06",
            "title": "High school faculty domain overlap",
            "ambiguity_type": "shared_domain",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Arthur Vance",
                    "canonical_email": "a.vance@lincoln-hs.edu",
                    "canonical_phone": "+14025553601"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Elena Gomez",
                    "canonical_email": "e.gomez@lincoln-hs.edu",
                    "canonical_phone": "+14025553602"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-02T08:00:00Z",
                    "channel": "email",
                    "sender_email": "a.vance@lincoln-hs.edu",
                    "sender_phone": None,
                    "display_name": "Arthur Vance",
                    "text": "Science lab safety goggles and chemical storage cabinet order. Phone +14025553601.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-02T08:20:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+14025553601",
                    "display_name": None,
                    "text": "Arthur Vance: chemistry department shipment arriving at dock B.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-02T09:00:00Z",
                    "channel": "email",
                    "sender_email": "e.gomez@lincoln-hs.edu",
                    "sender_phone": None,
                    "display_name": "Elena Gomez",
                    "text": "Calculus textbooks and graphing calculator purchase requisition. Phone +14025553602.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-02T09:30:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+14025553602",
                    "display_name": None,
                    "text": "Elena Gomez calling to check status on graphing calculator licenses.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "test_07",
            "title": "Emergency locksmith neighbour phone",
            "ambiguity_type": "name_only",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Brian O'Connor",
                    "canonical_email": "brian.oconnor@fasttrack.com",
                    "canonical_phone": "+13105553701"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-02T19:00:00Z",
                    "channel": "email",
                    "sender_email": "brian.oconnor@fasttrack.com",
                    "sender_phone": None,
                    "display_name": "Brian O'Connor",
                    "text": "Key duplication and deadbolt lock repair request for unit 12. Cell +13105553701.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-02T19:15:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+13105553701",
                    "display_name": None,
                    "text": "Brian O'Connor here, locked out of unit 12, need technician asap.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-02T19:40:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": None,
                    "display_name": None,
                    "text": "This is Brian O'Connor calling from neighbour phone, technician hasn't arrived yet.",
                    "true_identity_id": "user_1"
                }
            ]
        },
        {
            "scenario_id": "test_08",
            "title": "Automobile insurance claim adjustment",
            "ambiguity_type": "none",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Nathan Drake",
                    "canonical_email": "nathan.drake@uncharted.com",
                    "canonical_phone": "+14155553801"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-02T11:00:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+14155553801",
                    "display_name": None,
                    "text": "Nathan Drake calling to report rear bumper collision on Highway 1. Email is nathan.drake@uncharted.com.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-02T11:20:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+14155553801",
                    "display_name": None,
                    "text": "Nathan Drake: claim number CLM7782 assigned for bumper collision.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-02T11:45:00Z",
                    "channel": "email",
                    "sender_email": "nathan.drake@uncharted.com",
                    "sender_phone": None,
                    "display_name": "Nathan Drake",
                    "text": "Accident damage photos and repair shop estimate for claim CLM7782. Mobile +14155553801.",
                    "true_identity_id": "user_1"
                }
            ]
        },
        {
            "scenario_id": "test_09",
            "title": "Broadband shared apartment phone",
            "ambiguity_type": "reused_phone",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Tom Sawyer",
                    "canonical_email": "tom.sawyer@river.org",
                    "canonical_phone": "+12125553900"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Jerry Finn",
                    "canonical_email": "jerry.finn@river.org",
                    "canonical_phone": "+12125553900"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-02T14:00:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+12125553900",
                    "display_name": None,
                    "text": "Tom Sawyer calling to upgrade apartment internet router to fiber gigabit. Account tom.sawyer@river.org.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-02T14:15:00Z",
                    "channel": "email",
                    "sender_email": "tom.sawyer@river.org",
                    "sender_phone": None,
                    "display_name": "Tom Sawyer",
                    "text": "Account verification for fiber gigabit installation at unit 5. Tom Sawyer.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-02T15:00:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+12125553900",
                    "display_name": None,
                    "text": "Hi this is Jerry Finn, roommate of Tom, asking if technician brings cables. Email jerry.finn@river.org.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-02T15:30:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+12125553900",
                    "display_name": None,
                    "text": "Jerry Finn calling back, need Saturday technician installation slot for broadband.",
                    "true_identity_id": "user_2"
                }
            ]
        },
        {
            "scenario_id": "test_10",
            "title": "Enterprise sales and engineering domain overlap",
            "ambiguity_type": "shared_domain",
            "true_identities": [
                {
                    "identity_id": "user_1",
                    "canonical_name": "Olivia Wilde",
                    "canonical_email": "olivia.wilde@enterprise-ai.co",
                    "canonical_phone": "+14155554001"
                },
                {
                    "identity_id": "user_2",
                    "canonical_name": "Ethan Hunt",
                    "canonical_email": "ethan.hunt@enterprise-ai.co",
                    "canonical_phone": "+14155554002"
                }
            ],
            "messages": [
                {
                    "message_id": "m1",
                    "timestamp": "2026-10-02T16:00:00Z",
                    "channel": "email",
                    "sender_email": "olivia.wilde@enterprise-ai.co",
                    "sender_phone": None,
                    "display_name": "Olivia Wilde",
                    "text": "Enterprise licensing contract renewal and customer success review. Cell +14155554001.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m2",
                    "timestamp": "2026-10-02T16:20:00Z",
                    "channel": "sms",
                    "sender_email": None,
                    "sender_phone": "+14155554001",
                    "display_name": None,
                    "text": "Olivia Wilde: customer signed enterprise MSA agreement.",
                    "true_identity_id": "user_1"
                },
                {
                    "message_id": "m3",
                    "timestamp": "2026-10-02T17:00:00Z",
                    "channel": "email",
                    "sender_email": "ethan.hunt@enterprise-ai.co",
                    "sender_phone": None,
                    "display_name": "Ethan Hunt",
                    "text": "Technical architecture specification for on-premise GPU cluster deployment. Direct +14155554002.",
                    "true_identity_id": "user_2"
                },
                {
                    "message_id": "m4",
                    "timestamp": "2026-10-02T17:30:00Z",
                    "channel": "voice",
                    "sender_email": None,
                    "sender_phone": "+14155554002",
                    "display_name": None,
                    "text": "Ethan Hunt calling to discuss GPU driver compatibility with customer cluster.",
                    "true_identity_id": "user_2"
                }
            ]
        }
    ]

    test_dir = Path("data/test")
    test_dir.mkdir(parents=True, exist_ok=True)
    for s in scenarios:
        path = test_dir / f"{s['scenario_id']}.yaml"
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(s, f, sort_keys=False)

def generate_second_pass():
    second_pass = {
        "dev_01": {"m1": "user_1", "m2": "user_2", "m3": "user_1", "m4": "user_2"},
        "dev_02": {"m1": "user_1", "m2": "user_1", "m3": "user_2", "m4": "user_2"},
        "dev_03": {"m1": "user_1", "m2": "user_1", "m3": "user_1", "m4": "user_2"},
        "dev_04": {"m1": "user_1", "m2": "user_1", "m3": "user_1"},
        "dev_05": {"m1": "user_1", "m2": "user_1", "m3": "user_2", "m4": "user_2"},
        "dev_06": {"m1": "user_1", "m2": "user_1", "m3": "user_2", "m4": "user_2"},
        "dev_07": {"m1": "user_1", "m2": "user_1", "m3": "user_1"},
        "dev_08": {"m1": "user_1", "m2": "user_1", "m3": "user_1"},
        "dev_09": {"m1": "user_1", "m2": "user_1", "m3": "user_2", "m4": "user_2"},
        "dev_10": {"m1": "user_1", "m2": "user_1", "m3": "user_2", "m4": "user_2"}
    }
    with open("data/dev_second_pass.yaml", "w", encoding="utf-8") as f:
        yaml.dump(second_pass, f, sort_keys=False)

if __name__ == "__main__":
    generate_dev_scenarios()
    generate_test_scenarios()
    generate_second_pass()
