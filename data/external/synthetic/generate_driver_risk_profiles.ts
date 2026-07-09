// Files DB
// const filesDb = database("c1c8389a-68fe-4a97-98ba-b62f74daab3e");

const N_PER_CLASS = 10000;
const CLASSES = ["Slight", "Serious", "Fatal"] as const;
type Sev = (typeof CLASSES)[number];

// Weighted sampler
type W = Record<string, number>;
function pick(w: W): string {
  let total = 0;
  for (const k in w) total += w[k];
  let r = Math.random() * total;
  for (const k in w) {
    r -= w[k];
    if (r <= 0) return k;
  }
  return Object.keys(w)[0];
}

// Class-conditional distributions. Each field has a per-severity weight map.
// Encodes the Rwandan-context generation policy (synthetic, not ground-truth crash data).
const dist: Record<string, Record<Sev, W>> = {
  driver_age_band: {
    Slight: {
      "Under 18": 0.03,
      "18-30": 0.42,
      "31-50": 0.44,
      "Over 51": 0.07,
      Unknown: 0.04,
    },
    Serious: {
      "Under 18": 0.05,
      "18-30": 0.46,
      "31-50": 0.39,
      "Over 51": 0.06,
      Unknown: 0.04,
    },
    Fatal: {
      "Under 18": 0.06,
      "18-30": 0.5,
      "31-50": 0.34,
      "Over 51": 0.06,
      Unknown: 0.04,
    },
  },
  driver_sex: {
    Slight: { Male: 0.89, Female: 0.1, Unknown: 0.01 },
    Serious: { Male: 0.9, Female: 0.09, Unknown: 0.01 },
    Fatal: { Male: 0.92, Female: 0.07, Unknown: 0.01 },
  },
  driver_experience: {
    Slight: {
      "No Licence": 0.05,
      "Below 1yr": 0.08,
      "1-2yr": 0.12,
      "2-5yr": 0.2,
      "5-10yr": 0.25,
      "Above 10yr": 0.25,
      Unknown: 0.05,
    },
    Serious: {
      "No Licence": 0.1,
      "Below 1yr": 0.18,
      "1-2yr": 0.22,
      "2-5yr": 0.2,
      "5-10yr": 0.15,
      "Above 10yr": 0.1,
      Unknown: 0.05,
    },
    Fatal: {
      "No Licence": 0.15,
      "Below 1yr": 0.22,
      "1-2yr": 0.24,
      "2-5yr": 0.16,
      "5-10yr": 0.1,
      "Above 10yr": 0.08,
      Unknown: 0.05,
    },
  },
  driver_education: {
    Slight: {
      Illiterate: 0.04,
      "Writing & reading": 0.09,
      "Elementary school": 0.19,
      "Junior high school": 0.22,
      "High school": 0.3,
      "Above high school": 0.13,
      Unknown: 0.03,
    },
    Serious: {
      Illiterate: 0.05,
      "Writing & reading": 0.11,
      "Elementary school": 0.21,
      "Junior high school": 0.22,
      "High school": 0.27,
      "Above high school": 0.11,
      Unknown: 0.03,
    },
    Fatal: {
      Illiterate: 0.07,
      "Writing & reading": 0.12,
      "Elementary school": 0.23,
      "Junior high school": 0.22,
      "High school": 0.24,
      "Above high school": 0.09,
      Unknown: 0.03,
    },
  },
  driver_vehicle_relation: {
    Slight: { Employee: 0.33, Owner: 0.47, Other: 0.15, Unknown: 0.05 },
    Serious: { Employee: 0.36, Owner: 0.43, Other: 0.16, Unknown: 0.05 },
    Fatal: { Employee: 0.38, Owner: 0.4, Other: 0.17, Unknown: 0.05 },
  },
  vehicle_type: {
    Slight: {
      Automobile: 0.4,
      "Public (12 seats)": 0.06,
      "Public (>45 seats)": 0.04,
      Lorry: 0.06,
      Motorcycle: 0.25,
      Bajaj: 0.12,
      Bicycle: 0.02,
      Other: 0.03,
      Unknown: 0.02,
    },
    Serious: {
      Automobile: 0.22,
      "Public (12 seats)": 0.05,
      "Public (>45 seats)": 0.04,
      Lorry: 0.06,
      Motorcycle: 0.42,
      Bajaj: 0.1,
      Bicycle: 0.06,
      Other: 0.03,
      Unknown: 0.02,
    },
    Fatal: {
      Automobile: 0.15,
      "Public (12 seats)": 0.05,
      "Public (>45 seats)": 0.05,
      Lorry: 0.07,
      Motorcycle: 0.48,
      Bajaj: 0.08,
      Bicycle: 0.08,
      Other: 0.02,
      Unknown: 0.02,
    },
  },
  vehicle_owner: {
    Slight: {
      Owner: 0.57,
      Governmental: 0.11,
      Organization: 0.2,
      Other: 0.07,
      Unknown: 0.05,
    },
    Serious: {
      Owner: 0.55,
      Governmental: 0.12,
      Organization: 0.2,
      Other: 0.08,
      Unknown: 0.05,
    },
    Fatal: {
      Owner: 0.53,
      Governmental: 0.13,
      Organization: 0.2,
      Other: 0.09,
      Unknown: 0.05,
    },
  },
  vehicle_service_year: {
    Slight: {
      "Below 1yr": 0.12,
      "1-2yr": 0.18,
      "2-5yrs": 0.28,
      "5-10yrs": 0.22,
      "Above 10yr": 0.12,
      Unknown: 0.08,
    },
    Serious: {
      "Below 1yr": 0.08,
      "1-2yr": 0.12,
      "2-5yrs": 0.2,
      "5-10yrs": 0.3,
      "Above 10yr": 0.22,
      Unknown: 0.08,
    },
    Fatal: {
      "Below 1yr": 0.05,
      "1-2yr": 0.08,
      "2-5yrs": 0.15,
      "5-10yrs": 0.32,
      "Above 10yr": 0.32,
      Unknown: 0.08,
    },
  },
  vehicle_defect: {
    Slight: { "No defect": 0.88, "5": 0.04, "7": 0.03, Unknown: 0.05 },
    Serious: { "No defect": 0.78, "5": 0.09, "7": 0.08, Unknown: 0.05 },
    Fatal: { "No defect": 0.7, "5": 0.13, "7": 0.12, Unknown: 0.05 },
  },
  weather: {
    Slight: {
      Normal: 0.7,
      Raining: 0.08,
      Windy: 0.05,
      Cloudy: 0.1,
      Other: 0.03,
      Unknown: 0.04,
    },
    Serious: {
      Normal: 0.5,
      Raining: 0.25,
      Windy: 0.06,
      Cloudy: 0.12,
      Other: 0.03,
      Unknown: 0.04,
    },
    Fatal: {
      Normal: 0.42,
      Raining: 0.33,
      Windy: 0.06,
      Cloudy: 0.12,
      Other: 0.03,
      Unknown: 0.04,
    },
  },
  road_surface: {
    Slight: {
      Asphalt: 0.75,
      Gravel: 0.12,
      Earth: 0.06,
      Other: 0.03,
      Unknown: 0.04,
    },
    Serious: {
      Asphalt: 0.5,
      Gravel: 0.28,
      Earth: 0.15,
      Other: 0.03,
      Unknown: 0.04,
    },
    Fatal: {
      Asphalt: 0.4,
      Gravel: 0.32,
      Earth: 0.21,
      Other: 0.03,
      Unknown: 0.04,
    },
  },
  light_condition: {
    Slight: {
      Daylight: 0.8,
      "Darkness - lit": 0.1,
      "Darkness - unlit": 0.05,
      Unknown: 0.05,
    },
    Serious: {
      Daylight: 0.55,
      "Darkness - lit": 0.18,
      "Darkness - unlit": 0.22,
      Unknown: 0.05,
    },
    Fatal: {
      Daylight: 0.42,
      "Darkness - lit": 0.16,
      "Darkness - unlit": 0.37,
      Unknown: 0.05,
    },
  },
  time_of_day: {
    Slight: { Morning: 0.35, Afternoon: 0.4, Evening: 0.18, Night: 0.07 },
    Serious: { Morning: 0.25, Afternoon: 0.3, Evening: 0.25, Night: 0.2 },
    Fatal: { Morning: 0.2, Afternoon: 0.25, Evening: 0.27, Night: 0.28 },
  },
};

const FIELDS = Object.keys(dist);

// let done = 0;
// const TOTAL = N_PER_CLASS * CLASSES.length;
// for (const sev of CLASSES) {
//   const rows: Record<string, string>[] = [];
//   for (let i = 0; i < N_PER_CLASS; i++) {
//     const row: Record<string, string> = {};
//     for (const f of FIELDS) row[f] = pick(dist[f][sev]);
//     row["synthetic_severity_label"] = sev;
//     rows.push(row);
//     done++;
//     sendProgressUpdate(`Generating ${sev} records`, Math.round((done / TOTAL) * 100));
//   }
//   filesDb.batchInsert("driver_risk_profiles", rows);
// }

// const count = await filesDb.query("SELECT COUNT(*) AS c FROM driver_risk_profiles");
// sendResult({ inserted: count[0].c });
