// Run in mongosh connected to a TEST database / local replica set.
// All records in this script are synthetic. Do not use production credentials.
const bank = db.getSiblingDB("meridian_bank_nosql");

bank.customer_profiles.deleteMany({ customerId: { $in: ["CUST0001", "CUST0002"] } });
bank.transfer_events.deleteMany({ reference: "MERIDIAN-DEMO-001" });
bank.accounts.deleteMany({ accountId: { $in: ["ACC0001", "ACC0002"] } });

bank.customer_profiles.insertMany([
  {
    _id: "CUS0001", customerId: "CUST0001",
    name: { first: "Amina", last: "Demo" },
    contact: { email: "amina@example.test", phone: "08000000001" },
    kyc: { status: "VERIFIED", level: 2 },
    accountSummaries: [{ accountId: "ACC0001", maskedNumber: "********0001", type: "SAVINGS", currency: "NGN", status: "ACTIVE" }],
    recentTransfers: [], updatedAt: new Date()
  },
  {
    _id: "CUS0002", customerId: "CUST0002",
    name: { first: "Tunde", last: "Demo" },
    contact: { email: "tunde@example.test", phone: "08000000002" },
    kyc: { status: "VERIFIED", level: 2 },
    accountSummaries: [{ accountId: "ACC0002", maskedNumber: "********0002", type: "CURRENT", currency: "NGN", status: "ACTIVE" }],
    recentTransfers: [], updatedAt: new Date()
  }
]);

bank.accounts.insertMany([
  { _id: "ACC0001", accountId: "ACC0001", customerId: "CUST0001", balanceKobo: 100000000, currency: "NGN", status: "ACTIVE" },
  { _id: "ACC0002", accountId: "ACC0002", customerId: "CUST0002", balanceKobo: 100000000, currency: "NGN", status: "ACTIVE" }
]);
bank.transfer_events.createIndex({ reference: 1 }, { unique: true });
bank.transfer_events.createIndex({ customerId: 1, createdAt: -1 });
bank.ledger_entries.createIndex({ transferId: 1, accountId: 1 });
bank.customer_profiles.createIndex({ customerId: 1 }, { unique: true });

// Dashboard lookup: embedded profile attributes + recent transfers in one document read.
printjson(bank.customer_profiles.findOne(
  { customerId: "CUST0001" },
  { _id: 0, customerId: 1, name: 1, accountSummaries: 1, recentTransfers: 1 }
));

// Operational activity feed query, supported by the compound index.
printjson(bank.transfer_events.find({ customerId: "CUST0001" }).sort({ createdAt: -1 }).limit(20).explain("executionStats"));

// Multi-document atomic transfer example. Transactions require a replica set or sharded cluster.
const session = db.getMongo().startSession();
try {
  session.startTransaction();
  const txdb = session.getDatabase("meridian_bank_nosql");
  const amount = 25000;
  const debit = txdb.accounts.updateOne(
    { accountId: "ACC0001", status: "ACTIVE", balanceKobo: { $gte: amount } },
    { $inc: { balanceKobo: -amount } }
  );
  if (debit.modifiedCount !== 1) throw new Error("Debit account missing, inactive, or insufficient funds");
  const credit = txdb.accounts.updateOne(
    { accountId: "ACC0002", status: "ACTIVE" },
    { $inc: { balanceKobo: amount } }
  );
  if (credit.modifiedCount !== 1) throw new Error("Credit account missing or inactive");
  txdb.transfer_events.insertOne({
    _id: "TRF-DOC-001", reference: "MERIDIAN-DEMO-001", customerId: "CUST0001",
    debitAccountId: "ACC0001", creditAccountId: "ACC0002", amountKobo: amount,
    currency: "NGN", status: "COMPLETED", createdAt: new Date(),
    metadata: { channel: "MOBILE", narration: "Demo transfer" }
  });
  txdb.ledger_entries.insertMany([
    { transferId: "TRF-DOC-001", accountId: "ACC0001", direction: "DEBIT", amountKobo: amount, postedAt: new Date() },
    { transferId: "TRF-DOC-001", accountId: "ACC0002", direction: "CREDIT", amountKobo: amount, postedAt: new Date() }
  ]);
  session.commitTransaction();
  print("MongoDB transfer committed");
} catch (error) {
  session.abortTransaction();
  print("MongoDB transfer aborted: " + error.message);
} finally {
  session.endSession();
}
