"""
Test script for Email Understanding & Action Bot
Tests classification with sample emails
"""
import os
from email_classifier import EmailClassifier
from email_bot_database import EmailBotDatabase

def test_classification():
    """Test email classification with sample emails"""
    
    # Initialize
    api_key = os.getenv('OPENAI_API_KEY', '')
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set!")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        return
    
    classifier = EmailClassifier(api_key=api_key)
    db = EmailBotDatabase()
    categories = db.get_all_categories()
    
    print("=" * 80)
    print("Email Understanding & Action Bot - Classification Test")
    print("=" * 80)
    print()
    
    # Test emails
    test_emails = [
        {
            "name": "Invoice Email",
            "subject": "Invoice #12345 - Payment Due",
            "body": "Dear Customer,\n\nPlease find attached invoice for services rendered.\n\nInvoice Number: INV-12345\nAmount: $5,000.00\nDue Date: December 31, 2024\nPayment Terms: Net 30\n\nPlease remit payment by the due date.\n\nThank you,\nAccounts Receivable",
            "sender": "billing@vendor.com"
        },
        {
            "name": "Leave Request",
            "subject": "Vacation Request - December 20-27",
            "body": "Hi HR Team,\n\nI would like to request time off for vacation from December 20 to December 27, 2024.\n\nThis is for a family trip. I have sufficient leave balance.\n\nPlease approve this request.\n\nThanks,\nJohn Doe",
            "sender": "john.doe@company.com"
        },
        {
            "name": "Meeting Request",
            "subject": "Meeting: Q4 Review - Dec 15, 2 PM",
            "body": "Hi Team,\n\nI'd like to schedule a meeting to review our Q4 performance.\n\nDate: December 15, 2024\nTime: 2:00 PM - 3:00 PM\nLocation: Conference Room A\n\nPlease confirm your availability.\n\nBest regards,\nManager",
            "sender": "manager@company.com"
        },
        {
            "name": "Support Ticket",
            "subject": "Issue with Login - Urgent",
            "body": "Hello Support,\n\nI'm experiencing an issue logging into the system. I keep getting an error message.\n\nError: 'Invalid credentials'\n\nI've tried resetting my password but the issue persists. Can you please help?\n\nThanks,\nUser",
            "sender": "user@customer.com"
        },
        {
            "name": "Purchase Order",
            "subject": "PO #PO-2024-001 - Office Supplies",
            "body": "Dear Vendor,\n\nPlease find our purchase order for office supplies.\n\nPO Number: PO-2024-001\nItems: Office chairs, desks, stationery\nTotal Amount: $10,000\nDelivery Date: January 15, 2025\n\nPlease confirm receipt.\n\nProcurement Team",
            "sender": "procurement@company.com"
        },
        {
            "name": "Expense Report",
            "subject": "Expense Report - November 2024",
            "body": "Hi Finance,\n\nPlease find my expense report for November 2024.\n\nTotal Expenses: $1,250.00\nCategories:\n- Travel: $800\n- Meals: $300\n- Supplies: $150\n\nReceipts attached.\n\nThanks,\nEmployee",
            "sender": "employee@company.com"
        },
        {
            "name": "Contract Review",
            "subject": "Contract Review Request - Vendor Agreement",
            "body": "Hi Legal Team,\n\nI need your review of a vendor agreement before we sign.\n\nContract Type: Service Agreement\nVendor: ABC Services Inc.\nValue: $50,000 annually\n\nPlease review the attached contract and provide feedback.\n\nThanks,\nProcurement",
            "sender": "procurement@company.com"
        },
        {
            "name": "General Inquiry",
            "subject": "Question about Company Policy",
            "body": "Hello,\n\nI have a question about the company's remote work policy. Can you provide more information?\n\nThanks,\nEmployee",
            "sender": "employee@company.com"
        },
        {
            "name": "Invoice with Attachment",
            "subject": "Invoice Attached - Payment Required",
            "body": "Please see attached invoice for payment.\n\nDue date: 2024-12-31\nAmount: $3,500\n\nThank you.",
            "sender": "billing@supplier.com"
        },
        {
            "name": "Time Off Request",
            "subject": "Sick Leave - Today",
            "body": "Hi,\n\nI need to take a sick day today. I'm not feeling well.\n\nI'll be back tomorrow.\n\nThanks,\nEmployee",
            "sender": "employee@company.com"
        }
    ]
    
    results = []
    
    for i, test_email in enumerate(test_emails, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(test_emails)}: {test_email['name']}")
        print(f"{'='*80}")
        print(f"Subject: {test_email['subject']}")
        print(f"From: {test_email['sender']}")
        print(f"\nBody:\n{test_email['body'][:200]}...")
        print("\n" + "-"*80)
        
        try:
            classification = classifier.classify_email(test_email, categories)
            
            print(f"\n✅ Classification Result:")
            print(f"   Category: {classification['category']}")
            print(f"   Confidence: {classification['confidence']:.1%}")
            print(f"   Action: {classification['action_name']} ({classification['action_type']})")
            print(f"   Target: {classification.get('target', 'N/A')}")
            print(f"   Justification: {classification['justification']}")
            
            results.append({
                'test': test_email['name'],
                'category': classification['category'],
                'confidence': classification['confidence'],
                'action': classification['action_name']
            })
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            results.append({
                'test': test_email['name'],
                'category': 'ERROR',
                'confidence': 0.0,
                'action': 'N/A'
            })
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"\nTotal Tests: {len(test_emails)}")
    print(f"Successful: {sum(1 for r in results if r['category'] != 'ERROR')}")
    print(f"Failed: {sum(1 for r in results if r['category'] == 'ERROR')}")
    print(f"Average Confidence: {sum(r['confidence'] for r in results) / len(results):.1%}")
    
    print("\n" + "-"*80)
    print("Detailed Results:")
    print("-"*80)
    for result in results:
        status = "✅" if result['category'] != 'ERROR' else "❌"
        print(f"{status} {result['test']:30} → {result['category']:25} ({result['confidence']:.1%})")
    
    print("\n" + "="*80)
    print("Test Complete!")
    print("="*80)

if __name__ == "__main__":
    test_classification()

