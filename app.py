import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional
import json

class HospitalManagementSystem:
    def __init__(self, connection_string="mongodb://localhost:27017/", db_name="hospital_db"):
        """Initialize the Hospital Management System with MongoDB connection"""
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[db_name]
            self.patients_collection = self.db["patients"]
            self.billing_collection = self.db["billing"]
            
   
            self.client.admin.command('ping')
            
     
            try:
                self.patients_collection.create_index("patient_id", unique=True)
                self.billing_collection.create_index("patient_id")
            except Exception as index_error:
         
                pass
            
            print("✅ Connected to MongoDB successfully!")
            print(f"📊 Database: {db_name}")
            
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            print("💡 Make sure MongoDB is running or check your connection string")
            raise

    def generate_patient_id(self) -> str:
        """Generate a unique patient ID"""
        return f"PAT{str(uuid.uuid4())[:8].upper()}"

    def patient_onboarding(self) -> str:
        """Handle patient onboarding process"""
        print("\n" + "="*50)
        print("        PATIENT ONBOARDING")
        print("="*50)
        
        try:

            print("Please enter patient information:")
            
            patient_data = {
                "patient_id": self.generate_patient_id(),
                "personal_info": {
                    "name": input("Enter patient name: ").strip(),
                    "age": int(input("Enter patient age: ")),
                    "gender": input("Enter gender (M/F/Other): ").strip(),
                    "phone": input("Enter phone number: ").strip(),
                    "address": input("Enter address: ").strip(),
                    "emergency_contact": input("Enter emergency contact: ").strip()
                },
                "medical_info": {
                    "disease": input("Enter disease/condition: ").strip(),
                    "symptoms": input("Enter symptoms: ").strip(),
                    "allergies": input("Enter allergies (if any): ").strip(),
                    "medical_history": input("Enter medical history: ").strip()
                },
                "admission_info": {
                    "admission_date": datetime.now(),
                    "admission_type": input("Enter admission type (Emergency/Regular/ICU): ").strip(),
                    "assigned_doctor": input("Enter assigned doctor name: ").strip(),
                    "room_number": input("Enter room number: ").strip(),
                    "status": "Active"
                },
                "billing_info": {
                    "total_amount": 0.0,
                    "paid_amount": 0.0,
                    "outstanding_amount": 0.0
                },
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
      
            result = self.patients_collection.insert_one(patient_data)
            
            if result.inserted_id:
                print(f"\n✅ Patient onboarded successfully!")
                print(f"🆔 Patient ID: {patient_data['patient_id']}")
                print(f"📅 Admission Date: {patient_data['admission_info']['admission_date'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"🏥 Room: {patient_data['admission_info']['room_number']}")
                print(f"👨‍⚕️ Doctor: {patient_data['admission_info']['assigned_doctor']}")
                return patient_data['patient_id']
            else:
                print("❌ Failed to onboard patient")
                return None
                
        except ValueError as e:
            print(f"❌ Invalid input: Please enter valid data")
            return None
        except Exception as e:
            print(f"❌ Error during onboarding: {e}")
            return None

    def patient_discharge(self, patient_id: str = None) -> bool:
        """Handle patient discharge process"""
        print("\n" + "="*50)
        print("        PATIENT DISCHARGE")
        print("="*50)
        
        try:
            if not patient_id:
                patient_id = input("Enter Patient ID: ").strip()
            
      
            patient = self.patients_collection.find_one({"patient_id": patient_id})
            
            if not patient:
                print("❌ Patient not found!")
                return False
            
            if patient["admission_info"]["status"] != "Active":
                print(f"❌ Patient is not currently active! Current status: {patient['admission_info']['status']}")
                return False
            
         
            print(f"\n📋 Patient Information:")
            print(f"   Name: {patient['personal_info']['name']}")
            print(f"   Disease: {patient['medical_info']['disease']}")
            print(f"   Admission Date: {patient['admission_info']['admission_date'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Room: {patient['admission_info']['room_number']}")
            print(f"   Doctor: {patient['admission_info']['assigned_doctor']}")
            
       
            confirm = input("\nDo you want to discharge this patient? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Discharge cancelled.")
                return False
            
          
            discharge_notes = input("Enter discharge notes: ").strip()
            
           
            discharge_data = {
                "admission_info.status": "Discharged",
                "admission_info.discharge_date": datetime.now(),
                "admission_info.discharge_notes": discharge_notes,
                "updated_at": datetime.now()
            }
            
            result = self.patients_collection.update_one(
                {"patient_id": patient_id},
                {"$set": discharge_data}
            )
            
            if result.modified_count > 0:
                print("✅ Patient discharged successfully!")
                print(f"📅 Discharge Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                return True
            else:
                print("❌ Failed to discharge patient")
                return False
                
        except Exception as e:
            print(f"❌ Error during discharge: {e}")
            return False

    def fee_calculator(self, patient_id: str = None) -> Dict:
        """Calculate and manage patient fees"""
        print("\n" + "="*50)
        print("        FEE CALCULATOR")
        print("="*50)
        
        try:
            if not patient_id:
                patient_id = input("Enter Patient ID: ").strip()
            
          
            patient = self.patients_collection.find_one({"patient_id": patient_id})
            
            if not patient:
                print("❌ Patient not found!")
                return None
            
            print(f"\n📋 Patient: {patient['personal_info']['name']}")
            print(f"🏥 Room: {patient['admission_info']['room_number']}")
            print(f"🩺 Condition: {patient['medical_info']['disease']}")
            
          
            admission_date = patient['admission_info']['admission_date']
            current_date = datetime.now()
            days_admitted = (current_date - admission_date).days + 1
            
           
            fee_structure = {
                "Emergency": {"room_per_day": 5000, "doctor_fee": 2000, "medicine_base": 1500},
                "Regular": {"room_per_day": 3000, "doctor_fee": 1500, "medicine_base": 1000},
                "ICU": {"room_per_day": 10000, "doctor_fee": 3000, "medicine_base": 2500}
            }
            
            admission_type = patient['admission_info']['admission_type']
            fees = fee_structure.get(admission_type, fee_structure["Regular"])
            
            
            room_charges = fees["room_per_day"] * days_admitted
            doctor_charges = fees["doctor_fee"]
            medicine_charges = fees["medicine_base"]
            
           
            print(f"\n📊 Base Charges (for {days_admitted} days):")
            print(f"   Room Charges: ₹{room_charges:,.2f}")
            print(f"   Doctor Charges: ₹{doctor_charges:,.2f}")
            print(f"   Medicine Charges: ₹{medicine_charges:,.2f}")
            
            print("\n--- Additional Charges ---")
            try:
                lab_charges = float(input("Enter lab test charges (0 if none): ") or "0")
                procedure_charges = float(input("Enter procedure charges (0 if none): ") or "0")
                pharmacy_charges = float(input("Enter additional pharmacy charges (0 if none): ") or "0")
            except ValueError:
                print("Invalid input for charges, setting to 0")
                lab_charges = procedure_charges = pharmacy_charges = 0
            
           
            total_amount = (room_charges + doctor_charges + medicine_charges + 
                          lab_charges + procedure_charges + pharmacy_charges)
            
            
            bill_breakdown = {
                "patient_id": patient_id,
                "patient_name": patient['personal_info']['name'],
                "admission_date": admission_date.strftime('%Y-%m-%d'),
                "days_admitted": days_admitted,
                "admission_type": admission_type,
                "charges": {
                    "room_charges": room_charges,
                    "doctor_charges": doctor_charges,
                    "medicine_charges": medicine_charges,
                    "lab_charges": lab_charges,
                    "procedure_charges": procedure_charges,
                    "pharmacy_charges": pharmacy_charges
                },
                "total_amount": total_amount,
                "generated_date": datetime.now(),
                "status": "Generated"
            }
            
            
            print("\n" + "="*50)
            print("           BILL BREAKDOWN")
            print("="*50)
            print(f"Patient ID: {patient_id}")
            print(f"Patient Name: {patient['personal_info']['name']}")
            print(f"Admission Type: {admission_type}")
            print(f"Days Admitted: {days_admitted}")
            print(f"Room Charges: ₹{room_charges:,.2f}")
            print(f"Doctor Charges: ₹{doctor_charges:,.2f}")
            print(f"Medicine Charges: ₹{medicine_charges:,.2f}")
            print(f"Lab Test Charges: ₹{lab_charges:,.2f}")
            print(f"Procedure Charges: ₹{procedure_charges:,.2f}")
            print(f"Pharmacy Charges: ₹{pharmacy_charges:,.2f}")
            print("-" * 50)
            print(f"💰 TOTAL AMOUNT: ₹{total_amount:,.2f}")
            print("="*50)
            
            
            existing_bill = self.billing_collection.find_one({"patient_id": patient_id})
            if existing_bill:
                
                self.billing_collection.update_one(
                    {"patient_id": patient_id},
                    {"$set": bill_breakdown}
                )
                print("📄 Bill updated in database")
            else:
                
                self.billing_collection.insert_one(bill_breakdown)
                print("📄 Bill saved to database")
            
        
            self.patients_collection.update_one(
                {"patient_id": patient_id},
                {"$set": {
                    "billing_info.total_amount": total_amount,
                    "billing_info.outstanding_amount": total_amount,
                    "updated_at": datetime.now()
                }}
            )
            print("📋 Patient billing info updated")
            
            return bill_breakdown
            
        except Exception as e:
            print(f"❌ Error calculating fees: {e}")
            return None

    def patient_information_status(self, patient_id: str = None) -> Dict:
        """Get complete patient information and status"""
        print("\n" + "="*50)
        print("      PATIENT INFORMATION STATUS")
        print("="*50)
        
        try:
            if not patient_id:
                patient_id = input("Enter Patient ID: ").strip()
            
        
            patient = self.patients_collection.find_one({"patient_id": patient_id})
            
            if not patient:
                print("❌ Patient not found!")
                return None
            
           
            print(f"\n{'='*60}")
            print(f"             PATIENT INFORMATION")
            print(f"{'='*60}")
            
          
            print(f"\n📋 PERSONAL INFORMATION:")
            print(f"   Patient ID: {patient['patient_id']}")
            print(f"   Name: {patient['personal_info']['name']}")
            print(f"   Age: {patient['personal_info']['age']}")
            print(f"   Gender: {patient['personal_info']['gender']}")
            print(f"   Phone: {patient['personal_info']['phone']}")
            print(f"   Address: {patient['personal_info']['address']}")
            print(f"   Emergency Contact: {patient['personal_info']['emergency_contact']}")
            
       
            print(f"\n🏥 MEDICAL INFORMATION:")
            print(f"   Disease/Condition: {patient['medical_info']['disease']}")
            print(f"   Symptoms: {patient['medical_info']['symptoms']}")
            print(f"   Allergies: {patient['medical_info']['allergies']}")
            print(f"   Medical History: {patient['medical_info']['medical_history']}")
         
            print(f"\n🛏️  ADMISSION INFORMATION:")
            print(f"   Admission Date: {patient['admission_info']['admission_date'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Admission Type: {patient['admission_info']['admission_type']}")
            print(f"   Assigned Doctor: {patient['admission_info']['assigned_doctor']}")
            print(f"   Room Number: {patient['admission_info']['room_number']}")
            print(f"   Status: {patient['admission_info']['status']}")
            
            if patient['admission_info']['status'] == 'Discharged':
                discharge_date = patient['admission_info'].get('discharge_date')
                if discharge_date:
                    print(f"   Discharge Date: {discharge_date.strftime('%Y-%m-%d %H:%M:%S')}")
                discharge_notes = patient['admission_info'].get('discharge_notes')
                if discharge_notes:
                    print(f"   Discharge Notes: {discharge_notes}")
            
          
            print(f"\n💰 BILLING INFORMATION:")
            print(f"   Total Amount: ₹{patient['billing_info']['total_amount']:,.2f}")
            print(f"   Paid Amount: ₹{patient['billing_info']['paid_amount']:,.2f}")
            print(f"   Outstanding Amount: ₹{patient['billing_info']['outstanding_amount']:,.2f}")
            
      
            admission_date = patient['admission_info']['admission_date']
            if patient['admission_info']['status'] == 'Active':
                stay_duration = (datetime.now() - admission_date).days + 1
                print(f"\n⏰ STAY DURATION: {stay_duration} days (ongoing)")
            else:
                discharge_date = patient['admission_info'].get('discharge_date', datetime.now())
                stay_duration = (discharge_date - admission_date).days + 1
                print(f"\n⏰ TOTAL STAY DURATION: {stay_duration} days")
            
         
            if 'updated_at' in patient:
                print(f"📅 Last Updated: {patient['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            print(f"{'='*60}")
            
            return patient
            
        except Exception as e:
            print(f"❌ Error retrieving patient information: {e}")
            return None

    def search_patients(self, search_term: str = None) -> List[Dict]:
        """Search patients by name or patient ID"""
        print("\n" + "="*50)
        print("         SEARCH PATIENTS")
        print("="*50)
        
        try:
            if not search_term:
                search_term = input("Enter patient name or ID to search: ").strip()
            
            if not search_term:
                print("❌ Please enter a search term")
                return []
            
           
            query = {
                "$or": [
                    {"patient_id": {"$regex": search_term, "$options": "i"}},
                    {"personal_info.name": {"$regex": search_term, "$options": "i"}}
                ]
            }
            
            patients = list(self.patients_collection.find(query))
            
            if not patients:
                print(f"❌ No patients found matching '{search_term}'!")
                return []
            
            print(f"\n✅ Found {len(patients)} patient(s) matching '{search_term}':")
            print("-" * 100)
            print(f"{'Status':<8} {'Patient ID':<12} {'Name':<20} {'Disease':<15} {'Room':<6} {'Doctor':<15}")
            print("-" * 100)
            
            for patient in patients:
                status_emoji = "🟢" if patient['admission_info']['status'] == 'Active' else "🔴"
                status_text = patient['admission_info']['status']
                patient_id = patient['patient_id']
                name = patient['personal_info']['name'][:18] + "..." if len(patient['personal_info']['name']) > 18 else patient['personal_info']['name']
                disease = patient['medical_info']['disease'][:13] + "..." if len(patient['medical_info']['disease']) > 13 else patient['medical_info']['disease']
                room = patient['admission_info']['room_number']
                doctor = patient['admission_info']['assigned_doctor'][:13] + "..." if len(patient['admission_info']['assigned_doctor']) > 13 else patient['admission_info']['assigned_doctor']
                
                print(f"{status_emoji} {status_text:<6} {patient_id:<12} {name:<20} {disease:<15} {room:<6} {doctor:<15}")
            
            print("-" * 100)
            
            return patients
            
        except Exception as e:
            print(f"❌ Error searching patients: {e}")
            return []

    def get_all_patients(self) -> List[Dict]:
        """Get all patients from database"""
        try:
            patients = list(self.patients_collection.find())
            return patients
        except Exception as e:
            print(f"❌ Error fetching patients: {e}")
            return []

    def update_patient_info(self, patient_id: str) -> bool:
        """Update patient information"""
        try:
            patient = self.patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                print("❌ Patient not found!")
                return False
            
            print(f"\nCurrent patient: {patient['personal_info']['name']}")
            print("What would you like to update?")
            print("1. Personal Information")
            print("2. Medical Information")
            print("3. Room/Doctor Assignment")
            
            choice = input("Enter choice (1-3): ").strip()
            update_data = {"updated_at": datetime.now()}
            
            if choice == '1':
               
                new_phone = input(f"Phone ({patient['personal_info']['phone']}): ").strip()
                if new_phone:
                    update_data["personal_info.phone"] = new_phone
                
                new_address = input(f"Address ({patient['personal_info']['address']}): ").strip()
                if new_address:
                    update_data["personal_info.address"] = new_address
                    
            elif choice == '2':
               
                new_symptoms = input(f"Symptoms ({patient['medical_info']['symptoms']}): ").strip()
                if new_symptoms:
                    update_data["medical_info.symptoms"] = new_symptoms
                    
            elif choice == '3':
             
                new_room = input(f"Room ({patient['admission_info']['room_number']}): ").strip()
                if new_room:
                    update_data["admission_info.room_number"] = new_room
                
                new_doctor = input(f"Doctor ({patient['admission_info']['assigned_doctor']}): ").strip()
                if new_doctor:
                    update_data["admission_info.assigned_doctor"] = new_doctor
            
            if len(update_data) > 1: 
                result = self.patients_collection.update_one(
                    {"patient_id": patient_id},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    print("✅ Patient information updated successfully!")
                    return True
                else:
                    print("❌ Failed to update patient information")
                    return False
            else:
                print("No changes made.")
                return False
                
        except Exception as e:
            print(f"❌ Error updating patient: {e}")
            return False

def main():
    """Main function to run the Hospital Management System"""
    try:

        print("🏥 Initializing Hospital Management System...")
        hms = HospitalManagementSystem()
        
        while True:
            print("\n" + "="*60)
            print("           HOSPITAL MANAGEMENT SYSTEM")
            print("="*60)
            print("1. Patient Onboarding")
            print("2. Patient Discharge")
            print("3. Fee Calculator")
            print("4. Patient Information Status")
            print("5. Search Patients")
            print("6. Update Patient Information")
            print("7. View All Patients")
            print("8. Exit")
            print("="*60)
            
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == '1':
                hms.patient_onboarding()
            
            elif choice == '2':
                hms.patient_discharge()
            
            elif choice == '3':
                hms.fee_calculator()
            
            elif choice == '4':
                hms.patient_information_status()
            
            elif choice == '5':
                hms.search_patients()
            
            elif choice == '6':
                patient_id = input("Enter Patient ID to update: ").strip()
                hms.update_patient_info(patient_id)
            
            elif choice == '7':
                patients = hms.get_all_patients()
                if patients:
                    print(f"\n📊 Total Patients: {len(patients)}")
                    for patient in patients:
                        status = "🟢" if patient['admission_info']['status'] == 'Active' else "🔴"
                        print(f"{status} {patient['patient_id']} - {patient['personal_info']['name']} - {patient['admission_info']['status']}")
                else:
                    print("No patients found in database.")
            
            elif choice == '8':
                print("\n👋 Thank you for using Hospital Management System!")
                print("Database connection closed successfully.")
                break
            
            else:
                print("❌ Invalid choice! Please select 1-8.")
            
            input("\nPress Enter to continue...")
    
    except KeyboardInterrupt:
        print("\n\n👋 System interrupted by user. Goodbye!")
    except Exception as e:
        print(f"❌ System error: {e}")
    finally:
 
        try:
            if 'hms' in locals():
                hms.client.close()
        except:
            pass

if __name__ == "__main__":
    main()