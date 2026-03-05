window.GROWTH_MODEL_DATA = {
  "metadata": {
    "title": "Growth Model",
    "description": "Global growth model with vertical switch for All, C&C, and Faith.",
    "currency": "USD",
    "unit": "M",
    "generated_at": "2026-03-05T10:09:00+00:00",
    "source_files": [
      "/Users/antonkulikov/Projects/fundraiseup/growth-modeling/_inputs/fru/2024_all_accounts_donations.csv",
      "/Users/antonkulikov/Projects/fundraiseup/growth-modeling/_inputs/fru/2025_all_orgs_dontations__fru_enriched.csv",
      "/Users/antonkulikov/Projects/fundraiseup/growth-modeling/_inputs/fru/All Accounts Volume by Source & Frequency (2025).csv",
      "/Users/antonkulikov/Projects/fundraiseup/growth-modeling/model/religious_cohorts_2024_2025.csv",
      "/Users/antonkulikov/Projects/fundraiseup/growth-modeling/_inputs/fru/FUNDRAISEUP sectors.csv"
    ]
  },
  "verticals": {
    "all": {
      "id": "all",
      "label": "All",
      "targets_gpv_m": {
        "2024": 1130.4,
        "2025": 1718.2,
        "2026": 2851.16,
        "2027": 4834.58,
        "2028": 8479.1
      },
      "historical": {
        "gpv": {
          "2024": 1130397714.0,
          "2025": 1718195933.0
        },
        "cohort_anchor_2025": {
          "legacy_contribution": 1491878514.0,
          "new_2025_contribution": 226317419.0,
          "legacy_one_time": 992557277.0,
          "legacy_recurring": 499321287.0,
          "new_one_time": 198939986.0,
          "new_recurring": 27377455.0
        },
        "one_time_recurring": {
          "2024": {
            "one_time": 782377917.0,
            "recurring": 348019886.0,
            "recurring_share": 0.31
          },
          "2025": {
            "one_time": 1191497263.0,
            "recurring": 526698742.0,
            "recurring_share": 0.31
          }
        },
        "legacy_observed_kpis": {
          "nrr_2024_to_2025": 1.32,
          "carryover_component_ratio": 0.42,
          "implied_existing_account_expansion_rate": 0.9
        }
      },
      "segmentation": {
        "distribution_2025": [
          {
            "id": "lt_100k",
            "label": "<0.1M",
            "account_count": 3539,
            "gpv_total": 66247663.0,
            "share_of_accounts": 72.36,
            "share_of_gpv": 3.86
          },
          {
            "id": "100k_500k",
            "label": "0.1-0.5M",
            "account_count": 856,
            "gpv_total": 200630209.0,
            "share_of_accounts": 17.5,
            "share_of_gpv": 11.68
          },
          {
            "id": "500k_1m",
            "label": "0.5-1M",
            "account_count": 219,
            "gpv_total": 156337954.0,
            "share_of_accounts": 4.48,
            "share_of_gpv": 9.1
          },
          {
            "id": "1m_5m",
            "label": "1-5M",
            "account_count": 220,
            "gpv_total": 444724182.0,
            "share_of_accounts": 4.5,
            "share_of_gpv": 25.88
          },
          {
            "id": "5m_10m",
            "label": "5-10M",
            "account_count": 33,
            "gpv_total": 230822926.0,
            "share_of_accounts": 0.67,
            "share_of_gpv": 13.43
          },
          {
            "id": "10m_plus",
            "label": "10M+",
            "account_count": 24,
            "gpv_total": 619432999.0,
            "share_of_accounts": 0.49,
            "share_of_gpv": 36.05
          }
        ],
        "new_accounts_distribution_2025": [
          {
            "id": "lt_100k",
            "label": "<0.1M",
            "account_count": 1117,
            "gpv_total": 15432001.0,
            "share_of_accounts": 80.59,
            "share_of_gpv": 6.82,
            "avg_year1_gpv": 13815.58,
            "median_year1_gpv": 3528.0
          },
          {
            "id": "100k_500k",
            "label": "0.1-0.5M",
            "account_count": 184,
            "gpv_total": 41012883.0,
            "share_of_accounts": 13.28,
            "share_of_gpv": 18.12,
            "avg_year1_gpv": 222896.1,
            "median_year1_gpv": 193759.0
          },
          {
            "id": "500k_1m",
            "label": "0.5-1M",
            "account_count": 42,
            "gpv_total": 29555127.0,
            "share_of_accounts": 3.03,
            "share_of_gpv": 13.06,
            "avg_year1_gpv": 703693.5,
            "median_year1_gpv": 680344.0
          },
          {
            "id": "1m_5m",
            "label": "1-5M",
            "account_count": 37,
            "gpv_total": 78996858.0,
            "share_of_accounts": 2.67,
            "share_of_gpv": 34.91,
            "avg_year1_gpv": 2135050.22,
            "median_year1_gpv": 1642725.0
          },
          {
            "id": "5m_10m",
            "label": "5-10M",
            "account_count": 5,
            "gpv_total": 35307386.0,
            "share_of_accounts": 0.36,
            "share_of_gpv": 15.6,
            "avg_year1_gpv": 7061477.2,
            "median_year1_gpv": 7044436.0
          },
          {
            "id": "10m_plus",
            "label": "10M+",
            "account_count": 1,
            "gpv_total": 26013164.0,
            "share_of_accounts": 0.07,
            "share_of_gpv": 11.49,
            "avg_year1_gpv": 26013164.0,
            "median_year1_gpv": 26013164.0
          }
        ]
      }
    },
    "cc": {
      "id": "cc",
      "label": "C&C",
      "targets_gpv_m": {
        "2024": 894.84,
        "2025": 1386.05,
        "2026": 2300.0,
        "2027": 3900.0,
        "2028": 6840.0
      },
      "historical": {
        "gpv": {
          "2024": 894841032.0,
          "2025": 1386051089.0
        },
        "cohort_anchor_2025": {
          "legacy_contribution": 1209897213.0,
          "new_2025_contribution": 176115083.0,
          "legacy_one_time": 849470403.0,
          "legacy_recurring": 360426859.0,
          "new_one_time": 158508881.0,
          "new_recurring": 17606221.0
        },
        "one_time_recurring": {
          "2024": {
            "one_time": 659718132.0,
            "recurring": 235123001.0,
            "recurring_share": 0.26
          },
          "2025": {
            "one_time": 1007979284.0,
            "recurring": 378033080.0,
            "recurring_share": 0.27
          }
        },
        "legacy_observed_kpis": {
          "nrr_2024_to_2025": 1.35,
          "carryover_component_ratio": 0.42,
          "implied_existing_account_expansion_rate": 0.94
        }
      },
      "segmentation": {
        "distribution_2025": [
          {
            "id": "lt_100k",
            "label": "<0.1M",
            "account_count": 3436,
            "gpv_total": 62854891.0,
            "share_of_accounts": 73.97,
            "share_of_gpv": 4.53
          },
          {
            "id": "100k_500k",
            "label": "0.1-0.5M",
            "account_count": 785,
            "gpv_total": 182291123.0,
            "share_of_accounts": 16.9,
            "share_of_gpv": 13.15
          },
          {
            "id": "500k_1m",
            "label": "0.5-1M",
            "account_count": 190,
            "gpv_total": 136685163.0,
            "share_of_accounts": 4.09,
            "share_of_gpv": 9.86
          },
          {
            "id": "1m_5m",
            "label": "1-5M",
            "account_count": 183,
            "gpv_total": 369262867.0,
            "share_of_accounts": 3.94,
            "share_of_gpv": 26.64
          },
          {
            "id": "5m_10m",
            "label": "5-10M",
            "account_count": 31,
            "gpv_total": 217421151.0,
            "share_of_accounts": 0.67,
            "share_of_gpv": 15.69
          },
          {
            "id": "10m_plus",
            "label": "10M+",
            "account_count": 20,
            "gpv_total": 417497101.0,
            "share_of_accounts": 0.43,
            "share_of_gpv": 30.12
          }
        ],
        "new_accounts_distribution_2025": [
          {
            "id": "lt_100k",
            "label": "<0.1M",
            "account_count": 1087,
            "gpv_total": 14681061.0,
            "share_of_accounts": 82.04,
            "share_of_gpv": 8.34,
            "avg_year1_gpv": 13506.04,
            "median_year1_gpv": 3404.0
          },
          {
            "id": "100k_500k",
            "label": "0.1-0.5M",
            "account_count": 168,
            "gpv_total": 37000653.0,
            "share_of_accounts": 12.68,
            "share_of_gpv": 21.01,
            "avg_year1_gpv": 220241.98,
            "median_year1_gpv": 190521.0
          },
          {
            "id": "500k_1m",
            "label": "0.5-1M",
            "account_count": 35,
            "gpv_total": 24660138.0,
            "share_of_accounts": 2.64,
            "share_of_gpv": 14.0,
            "avg_year1_gpv": 704575.37,
            "median_year1_gpv": 686347.0
          },
          {
            "id": "1m_5m",
            "label": "1-5M",
            "account_count": 30,
            "gpv_total": 64465845.0,
            "share_of_accounts": 2.26,
            "share_of_gpv": 36.6,
            "avg_year1_gpv": 2148861.5,
            "median_year1_gpv": 1760324.5
          },
          {
            "id": "5m_10m",
            "label": "5-10M",
            "account_count": 5,
            "gpv_total": 35307386.0,
            "share_of_accounts": 0.38,
            "share_of_gpv": 20.05,
            "avg_year1_gpv": 7061477.2,
            "median_year1_gpv": 7044436.0
          },
          {
            "id": "10m_plus",
            "label": "10M+",
            "account_count": 0,
            "gpv_total": 0,
            "share_of_accounts": 0.0,
            "share_of_gpv": 0.0,
            "avg_year1_gpv": 0.0,
            "median_year1_gpv": 0.0
          }
        ]
      }
    },
    "faith": {
      "id": "faith",
      "label": "Faith",
      "targets_gpv_m": {
        "2024": 235.56,
        "2025": 332.14,
        "2026": 502.0,
        "2027": 860.0,
        "2028": 1480.0
      },
      "historical": {
        "gpv": {
          "2024": 235556682.0,
          "2025": 332144844.0
        },
        "cohort_anchor_2025": {
          "legacy_contribution": 281981301.0,
          "new_2025_contribution": 50202336.0,
          "legacy_one_time": 143086874.0,
          "legacy_recurring": 138894428.0,
          "new_one_time": 40431105.0,
          "new_recurring": 9771234.0
        },
        "one_time_recurring": {
          "2024": {
            "one_time": 122659785.0,
            "recurring": 112896885.0,
            "recurring_share": 0.48
          },
          "2025": {
            "one_time": 183517979.0,
            "recurring": 148665662.0,
            "recurring_share": 0.45
          }
        },
        "legacy_observed_kpis": {
          "nrr_2024_to_2025": 1.35,
          "carryover_component_ratio": 0.43,
          "implied_existing_account_expansion_rate": 0.92
        }
      },
      "segmentation": {
        "distribution_2025": [
          {
            "id": "lt_100k",
            "label": "<0.1M",
            "account_count": 103,
            "gpv_total": 3392772.0,
            "share_of_accounts": 41.87,
            "share_of_gpv": 1.02
          },
          {
            "id": "100k_500k",
            "label": "0.1-0.5M",
            "account_count": 71,
            "gpv_total": 18339086.0,
            "share_of_accounts": 28.86,
            "share_of_gpv": 5.52
          },
          {
            "id": "500k_1m",
            "label": "0.5-1M",
            "account_count": 29,
            "gpv_total": 19652791.0,
            "share_of_accounts": 11.79,
            "share_of_gpv": 5.92
          },
          {
            "id": "1m_5m",
            "label": "1-5M",
            "account_count": 37,
            "gpv_total": 75461315.0,
            "share_of_accounts": 15.04,
            "share_of_gpv": 22.72
          },
          {
            "id": "5m_10m",
            "label": "5-10M",
            "account_count": 2,
            "gpv_total": 13401775.0,
            "share_of_accounts": 0.81,
            "share_of_gpv": 4.03
          },
          {
            "id": "10m_plus",
            "label": "10M+",
            "account_count": 4,
            "gpv_total": 201935898.0,
            "share_of_accounts": 1.63,
            "share_of_gpv": 60.79
          }
        ],
        "new_accounts_distribution_2025": [
          {
            "id": "lt_100k",
            "label": "<0.1M",
            "account_count": 30,
            "gpv_total": 750940.0,
            "share_of_accounts": 49.18,
            "share_of_gpv": 1.5,
            "avg_year1_gpv": 25031.33,
            "median_year1_gpv": 14236.0
          },
          {
            "id": "100k_500k",
            "label": "0.1-0.5M",
            "account_count": 16,
            "gpv_total": 4012230.0,
            "share_of_accounts": 26.23,
            "share_of_gpv": 7.99,
            "avg_year1_gpv": 250764.38,
            "median_year1_gpv": 230303.0
          },
          {
            "id": "500k_1m",
            "label": "0.5-1M",
            "account_count": 7,
            "gpv_total": 4894989.0,
            "share_of_accounts": 11.48,
            "share_of_gpv": 9.75,
            "avg_year1_gpv": 699284.14,
            "median_year1_gpv": 669183.0
          },
          {
            "id": "1m_5m",
            "label": "1-5M",
            "account_count": 7,
            "gpv_total": 14531013.0,
            "share_of_accounts": 11.48,
            "share_of_gpv": 28.94,
            "avg_year1_gpv": 2075859.0,
            "median_year1_gpv": 1514532.0
          },
          {
            "id": "5m_10m",
            "label": "5-10M",
            "account_count": 0,
            "gpv_total": 0,
            "share_of_accounts": 0.0,
            "share_of_gpv": 0.0,
            "avg_year1_gpv": 0.0,
            "median_year1_gpv": 0.0
          },
          {
            "id": "10m_plus",
            "label": "10M+",
            "account_count": 1,
            "gpv_total": 26013164.0,
            "share_of_accounts": 1.64,
            "share_of_gpv": 51.82,
            "avg_year1_gpv": 26013164.0,
            "median_year1_gpv": 26013164.0
          }
        ]
      }
    }
  },
  "targets": {
    "cc_gpv_m": {
      "2024": 894.84,
      "2025": 1386.05,
      "2026": 2300.0,
      "2027": 3900.0,
      "2028": 6840.0
    },
    "take_rate": 0.03
  },
  "historical": {
    "all_gpv": {
      "2024": 1130397714.0,
      "2025": 1718195933.0
    },
    "faith_gpv": {
      "2024": 235556682.0,
      "2025": 332144844.0
    },
    "cc_gpv": {
      "2024": 894841032.0,
      "2025": 1386051089.0
    },
    "cohort_anchor_2025": {
      "legacy_contribution": 1209897213.0,
      "new_2025_contribution": 176115083.0,
      "legacy_one_time": 849470403.0,
      "legacy_recurring": 360426859.0,
      "new_one_time": 158508881.0,
      "new_recurring": 17606221.0
    },
    "cc_one_time_recurring": {
      "2024": {
        "one_time": 659718132.0,
        "recurring": 235123001.0,
        "recurring_share": 0.26
      },
      "2025": {
        "one_time": 1007979284.0,
        "recurring": 378033080.0,
        "recurring_share": 0.27
      }
    },
    "legacy_observed_kpis": {
      "nrr_2024_to_2025": 1.35,
      "carryover_component_ratio": 0.42,
      "implied_existing_account_expansion_rate": 0.94
    }
  },
  "segmentation": {
    "taxonomy": {
      "primary": "FRU Sector/Subsector",
      "secondary": "NTEE"
    },
    "coverage_2024_known_accounts": {
      "total_2024_accounts": 3799,
      "covered_by_2025_id": 2209,
      "covered_by_sector_domain": 0,
      "covered_by_sector_name": 65,
      "unclassified": 1525,
      "with_ntee_code": 1997,
      "with_fru_sector": 2019,
      "with_fru_subsector": 2019,
      "covered_total": 2274,
      "coverage_pct": 59.86,
      "ntee_coverage_pct": 52.57,
      "fru_sector_coverage_pct": 53.15,
      "fru_subsector_coverage_pct": 53.15
    },
    "analytical_brackets": [
      {
        "id": "lt_100k",
        "label": "<0.1M",
        "min": 0,
        "max": 100000
      },
      {
        "id": "100k_500k",
        "label": "0.1-0.5M",
        "min": 100000,
        "max": 500000
      },
      {
        "id": "500k_1m",
        "label": "0.5-1M",
        "min": 500000,
        "max": 1000000
      },
      {
        "id": "1m_5m",
        "label": "1-5M",
        "min": 1000000,
        "max": 5000000
      },
      {
        "id": "5m_10m",
        "label": "5-10M",
        "min": 5000000,
        "max": 10000000
      },
      {
        "id": "10m_plus",
        "label": "10M+",
        "min": 10000000,
        "max": null
      }
    ],
    "cc_2025_distribution": [
      {
        "id": "lt_100k",
        "label": "<0.1M",
        "account_count": 3436,
        "gpv_total": 62854891.0,
        "share_of_accounts": 73.97,
        "share_of_gpv": 4.53
      },
      {
        "id": "100k_500k",
        "label": "0.1-0.5M",
        "account_count": 785,
        "gpv_total": 182291123.0,
        "share_of_accounts": 16.9,
        "share_of_gpv": 13.15
      },
      {
        "id": "500k_1m",
        "label": "0.5-1M",
        "account_count": 190,
        "gpv_total": 136685163.0,
        "share_of_accounts": 4.09,
        "share_of_gpv": 9.86
      },
      {
        "id": "1m_5m",
        "label": "1-5M",
        "account_count": 183,
        "gpv_total": 369262867.0,
        "share_of_accounts": 3.94,
        "share_of_gpv": 26.64
      },
      {
        "id": "5m_10m",
        "label": "5-10M",
        "account_count": 31,
        "gpv_total": 217421151.0,
        "share_of_accounts": 0.67,
        "share_of_gpv": 15.69
      },
      {
        "id": "10m_plus",
        "label": "10M+",
        "account_count": 20,
        "gpv_total": 417497101.0,
        "share_of_accounts": 0.43,
        "share_of_gpv": 30.12
      }
    ],
    "cc_2025_new_accounts_distribution": [
      {
        "id": "lt_100k",
        "label": "<0.1M",
        "account_count": 1087,
        "gpv_total": 14681061.0,
        "share_of_accounts": 82.04,
        "share_of_gpv": 8.34,
        "avg_year1_gpv": 13506.04,
        "median_year1_gpv": 3404.0
      },
      {
        "id": "100k_500k",
        "label": "0.1-0.5M",
        "account_count": 168,
        "gpv_total": 37000653.0,
        "share_of_accounts": 12.68,
        "share_of_gpv": 21.01,
        "avg_year1_gpv": 220241.98,
        "median_year1_gpv": 190521.0
      },
      {
        "id": "500k_1m",
        "label": "0.5-1M",
        "account_count": 35,
        "gpv_total": 24660138.0,
        "share_of_accounts": 2.64,
        "share_of_gpv": 14.0,
        "avg_year1_gpv": 704575.37,
        "median_year1_gpv": 686347.0
      },
      {
        "id": "1m_5m",
        "label": "1-5M",
        "account_count": 30,
        "gpv_total": 64465845.0,
        "share_of_accounts": 2.26,
        "share_of_gpv": 36.6,
        "avg_year1_gpv": 2148861.5,
        "median_year1_gpv": 1760324.5
      },
      {
        "id": "5m_10m",
        "label": "5-10M",
        "account_count": 5,
        "gpv_total": 35307386.0,
        "share_of_accounts": 0.38,
        "share_of_gpv": 20.05,
        "avg_year1_gpv": 7061477.2,
        "median_year1_gpv": 7044436.0
      },
      {
        "id": "10m_plus",
        "label": "10M+",
        "account_count": 0,
        "gpv_total": 0,
        "share_of_accounts": 0.0,
        "share_of_gpv": 0.0,
        "avg_year1_gpv": 0.0,
        "median_year1_gpv": 0.0
      }
    ],
    "by_vertical": {
      "all": {
        "distribution_2025": [
          {
            "id": "lt_100k",
            "label": "<0.1M",
            "account_count": 3539,
            "gpv_total": 66247663.0,
            "share_of_accounts": 72.36,
            "share_of_gpv": 3.86
          },
          {
            "id": "100k_500k",
            "label": "0.1-0.5M",
            "account_count": 856,
            "gpv_total": 200630209.0,
            "share_of_accounts": 17.5,
            "share_of_gpv": 11.68
          },
          {
            "id": "500k_1m",
            "label": "0.5-1M",
            "account_count": 219,
            "gpv_total": 156337954.0,
            "share_of_accounts": 4.48,
            "share_of_gpv": 9.1
          },
          {
            "id": "1m_5m",
            "label": "1-5M",
            "account_count": 220,
            "gpv_total": 444724182.0,
            "share_of_accounts": 4.5,
            "share_of_gpv": 25.88
          },
          {
            "id": "5m_10m",
            "label": "5-10M",
            "account_count": 33,
            "gpv_total": 230822926.0,
            "share_of_accounts": 0.67,
            "share_of_gpv": 13.43
          },
          {
            "id": "10m_plus",
            "label": "10M+",
            "account_count": 24,
            "gpv_total": 619432999.0,
            "share_of_accounts": 0.49,
            "share_of_gpv": 36.05
          }
        ],
        "new_accounts_distribution_2025": [
          {
            "id": "lt_100k",
            "label": "<0.1M",
            "account_count": 1117,
            "gpv_total": 15432001.0,
            "share_of_accounts": 80.59,
            "share_of_gpv": 6.82,
            "avg_year1_gpv": 13815.58,
            "median_year1_gpv": 3528.0
          },
          {
            "id": "100k_500k",
            "label": "0.1-0.5M",
            "account_count": 184,
            "gpv_total": 41012883.0,
            "share_of_accounts": 13.28,
            "share_of_gpv": 18.12,
            "avg_year1_gpv": 222896.1,
            "median_year1_gpv": 193759.0
          },
          {
            "id": "500k_1m",
            "label": "0.5-1M",
            "account_count": 42,
            "gpv_total": 29555127.0,
            "share_of_accounts": 3.03,
            "share_of_gpv": 13.06,
            "avg_year1_gpv": 703693.5,
            "median_year1_gpv": 680344.0
          },
          {
            "id": "1m_5m",
            "label": "1-5M",
            "account_count": 37,
            "gpv_total": 78996858.0,
            "share_of_accounts": 2.67,
            "share_of_gpv": 34.91,
            "avg_year1_gpv": 2135050.22,
            "median_year1_gpv": 1642725.0
          },
          {
            "id": "5m_10m",
            "label": "5-10M",
            "account_count": 5,
            "gpv_total": 35307386.0,
            "share_of_accounts": 0.36,
            "share_of_gpv": 15.6,
            "avg_year1_gpv": 7061477.2,
            "median_year1_gpv": 7044436.0
          },
          {
            "id": "10m_plus",
            "label": "10M+",
            "account_count": 1,
            "gpv_total": 26013164.0,
            "share_of_accounts": 0.07,
            "share_of_gpv": 11.49,
            "avg_year1_gpv": 26013164.0,
            "median_year1_gpv": 26013164.0
          }
        ]
      },
      "cc": {
        "distribution_2025": [
          {
            "id": "lt_100k",
            "label": "<0.1M",
            "account_count": 3436,
            "gpv_total": 62854891.0,
            "share_of_accounts": 73.97,
            "share_of_gpv": 4.53
          },
          {
            "id": "100k_500k",
            "label": "0.1-0.5M",
            "account_count": 785,
            "gpv_total": 182291123.0,
            "share_of_accounts": 16.9,
            "share_of_gpv": 13.15
          },
          {
            "id": "500k_1m",
            "label": "0.5-1M",
            "account_count": 190,
            "gpv_total": 136685163.0,
            "share_of_accounts": 4.09,
            "share_of_gpv": 9.86
          },
          {
            "id": "1m_5m",
            "label": "1-5M",
            "account_count": 183,
            "gpv_total": 369262867.0,
            "share_of_accounts": 3.94,
            "share_of_gpv": 26.64
          },
          {
            "id": "5m_10m",
            "label": "5-10M",
            "account_count": 31,
            "gpv_total": 217421151.0,
            "share_of_accounts": 0.67,
            "share_of_gpv": 15.69
          },
          {
            "id": "10m_plus",
            "label": "10M+",
            "account_count": 20,
            "gpv_total": 417497101.0,
            "share_of_accounts": 0.43,
            "share_of_gpv": 30.12
          }
        ],
        "new_accounts_distribution_2025": [
          {
            "id": "lt_100k",
            "label": "<0.1M",
            "account_count": 1087,
            "gpv_total": 14681061.0,
            "share_of_accounts": 82.04,
            "share_of_gpv": 8.34,
            "avg_year1_gpv": 13506.04,
            "median_year1_gpv": 3404.0
          },
          {
            "id": "100k_500k",
            "label": "0.1-0.5M",
            "account_count": 168,
            "gpv_total": 37000653.0,
            "share_of_accounts": 12.68,
            "share_of_gpv": 21.01,
            "avg_year1_gpv": 220241.98,
            "median_year1_gpv": 190521.0
          },
          {
            "id": "500k_1m",
            "label": "0.5-1M",
            "account_count": 35,
            "gpv_total": 24660138.0,
            "share_of_accounts": 2.64,
            "share_of_gpv": 14.0,
            "avg_year1_gpv": 704575.37,
            "median_year1_gpv": 686347.0
          },
          {
            "id": "1m_5m",
            "label": "1-5M",
            "account_count": 30,
            "gpv_total": 64465845.0,
            "share_of_accounts": 2.26,
            "share_of_gpv": 36.6,
            "avg_year1_gpv": 2148861.5,
            "median_year1_gpv": 1760324.5
          },
          {
            "id": "5m_10m",
            "label": "5-10M",
            "account_count": 5,
            "gpv_total": 35307386.0,
            "share_of_accounts": 0.38,
            "share_of_gpv": 20.05,
            "avg_year1_gpv": 7061477.2,
            "median_year1_gpv": 7044436.0
          },
          {
            "id": "10m_plus",
            "label": "10M+",
            "account_count": 0,
            "gpv_total": 0,
            "share_of_accounts": 0.0,
            "share_of_gpv": 0.0,
            "avg_year1_gpv": 0.0,
            "median_year1_gpv": 0.0
          }
        ]
      },
      "faith": {
        "distribution_2025": [
          {
            "id": "lt_100k",
            "label": "<0.1M",
            "account_count": 103,
            "gpv_total": 3392772.0,
            "share_of_accounts": 41.87,
            "share_of_gpv": 1.02
          },
          {
            "id": "100k_500k",
            "label": "0.1-0.5M",
            "account_count": 71,
            "gpv_total": 18339086.0,
            "share_of_accounts": 28.86,
            "share_of_gpv": 5.52
          },
          {
            "id": "500k_1m",
            "label": "0.5-1M",
            "account_count": 29,
            "gpv_total": 19652791.0,
            "share_of_accounts": 11.79,
            "share_of_gpv": 5.92
          },
          {
            "id": "1m_5m",
            "label": "1-5M",
            "account_count": 37,
            "gpv_total": 75461315.0,
            "share_of_accounts": 15.04,
            "share_of_gpv": 22.72
          },
          {
            "id": "5m_10m",
            "label": "5-10M",
            "account_count": 2,
            "gpv_total": 13401775.0,
            "share_of_accounts": 0.81,
            "share_of_gpv": 4.03
          },
          {
            "id": "10m_plus",
            "label": "10M+",
            "account_count": 4,
            "gpv_total": 201935898.0,
            "share_of_accounts": 1.63,
            "share_of_gpv": 60.79
          }
        ],
        "new_accounts_distribution_2025": [
          {
            "id": "lt_100k",
            "label": "<0.1M",
            "account_count": 30,
            "gpv_total": 750940.0,
            "share_of_accounts": 49.18,
            "share_of_gpv": 1.5,
            "avg_year1_gpv": 25031.33,
            "median_year1_gpv": 14236.0
          },
          {
            "id": "100k_500k",
            "label": "0.1-0.5M",
            "account_count": 16,
            "gpv_total": 4012230.0,
            "share_of_accounts": 26.23,
            "share_of_gpv": 7.99,
            "avg_year1_gpv": 250764.38,
            "median_year1_gpv": 230303.0
          },
          {
            "id": "500k_1m",
            "label": "0.5-1M",
            "account_count": 7,
            "gpv_total": 4894989.0,
            "share_of_accounts": 11.48,
            "share_of_gpv": 9.75,
            "avg_year1_gpv": 699284.14,
            "median_year1_gpv": 669183.0
          },
          {
            "id": "1m_5m",
            "label": "1-5M",
            "account_count": 7,
            "gpv_total": 14531013.0,
            "share_of_accounts": 11.48,
            "share_of_gpv": 28.94,
            "avg_year1_gpv": 2075859.0,
            "median_year1_gpv": 1514532.0
          },
          {
            "id": "5m_10m",
            "label": "5-10M",
            "account_count": 0,
            "gpv_total": 0,
            "share_of_accounts": 0.0,
            "share_of_gpv": 0.0,
            "avg_year1_gpv": 0.0,
            "median_year1_gpv": 0.0
          },
          {
            "id": "10m_plus",
            "label": "10M+",
            "account_count": 1,
            "gpv_total": 26013164.0,
            "share_of_accounts": 1.64,
            "share_of_gpv": 51.82,
            "avg_year1_gpv": 26013164.0,
            "median_year1_gpv": 26013164.0
          }
        ]
      }
    }
  },
  "assumptions": {
    "recurring_donor_lifetime_months": 16,
    "annual_recurring_carryover": 0.46,
    "new_donor_year1_split": {
      "one_time": 0.7,
      "recurring": 0.3
    },
    "one_time_donor_year2_repeat_rate": 0.4,
    "existing_account_expansion_rate": 0.94,
    "cohort_year2_nrr": 1.35,
    "new_account_year1_to_year2_gpv_ratio": 1.0,
    "lt_100k_year1_gpv_per_logo_override_m": 0.05,
    "max_new_whales_per_year": 2,
    "bracket_mix_shift_2026_2028": "none"
  },
  "notes": [
    "2024 is treated as Legacy cohort because pre-2024 data is unavailable.",
    "Model supports vertical switch: All, C&C, Faith.",
    "Detailed phase-2 modeling will be by FRU Sector/Subsector.",
    "NTEE is retained for validation and reconciliation."
  ]
};
