#!/bin/bash

echo "Creating reports directory..."
mkdir -p api-testing/reports

echo ""
echo "======================================================="
echo "1. Running Auth Setup & Exporting Environment"
echo "======================================================="
npx newman run api-testing/EShop_API_Test_Suite.postman_collection.json -e api-testing/EShop_Environment.postman_environment.json --folder "Auth Setup" --export-environment api-testing/updated_env.json

echo ""
echo "======================================================="
echo "======================================================="
echo "2. Running FR-06 Cart Data-Driven Tests"
echo "======================================================="
npx newman run api-testing/EShop_API_Test_Suite.postman_collection.json -e api-testing/updated_env.json --folder "FR-06 Cart Data-Driven Tests (Run with FR06_Cart_DataDriven.json)" -d api-testing/FR06_Cart_DataDriven.json -r cli,htmlextra --reporter-htmlextra-export api-testing/reports/fr06_cart_datadriven.html

echo ""
echo "======================================================="
echo "3. Running FR-06 Cart Standalone Tests"
echo "======================================================="
npx newman run api-testing/EShop_API_Test_Suite.postman_collection.json -e api-testing/updated_env.json --folder "FR-06 Cart Standalone (ST, SEC, SCHEMA)" -r cli,htmlextra --reporter-htmlextra-export api-testing/reports/fr06_cart_standalone.html

echo ""
echo "======================================================="
echo "4. Running FR-11 Order Data-Driven Tests"
echo "======================================================="
npx newman run api-testing/EShop_API_Test_Suite.postman_collection.json -e api-testing/updated_env.json --folder "FR-11 Order Data-Driven Tests (Run with FR11_OrderHistory_DataDriven.json)" -d api-testing/FR11_OrderHistory_DataDriven.json -r cli,htmlextra --reporter-htmlextra-export api-testing/reports/fr11_orderhistory_datadriven.html

echo ""
echo "======================================================="
echo "5. Running FR-11 Order Standalone Tests"
echo "======================================================="
npx newman run api-testing/EShop_API_Test_Suite.postman_collection.json -e api-testing/updated_env.json --folder "FR-11 Order Standalone (ST, SEC, SCHEMA)" -r cli,htmlextra --reporter-htmlextra-export api-testing/reports/fr11_orderhistory_standalone.html

echo ""
echo "======================================================="
echo "6. Running FR-14 Category Data-Driven Tests"
echo "======================================================="
npx newman run api-testing/EShop_API_Test_Suite.postman_collection.json -e api-testing/updated_env.json --folder "FR-14 Category Data-Driven Tests (Run with FR14_Category_DataDriven.json)" -d api-testing/FR14_Category_DataDriven.json -r cli,htmlextra --reporter-htmlextra-export api-testing/reports/fr14_category_datadriven.html

echo ""
echo "======================================================="
echo "7. Running FR-14 Category Standalone Tests"
echo "======================================================="
npx newman run api-testing/EShop_API_Test_Suite.postman_collection.json -e api-testing/updated_env.json --folder "FR-14 Category Standalone (ST, SEC, SCHEMA)" -r cli,htmlextra --reporter-htmlextra-export api-testing/reports/fr14_category_standalone.html

echo ""
echo "======================================================="
echo "8. Running Extension Advanced Test Cases"
echo "======================================================="
npx newman run api-testing/EShop_API_Test_Suite.postman_collection.json -e api-testing/updated_env.json --folder "Extension: Advanced Test Cases" -r cli,htmlextra --reporter-htmlextra-export api-testing/reports/extension.html

echo ""
echo "======================================================="
echo "9. Running k6 Concurrency Tests"
echo "======================================================="
cd api-testing || exit
k6 run concurrency_k6_test.js
cd ..

echo ""
echo "======================================================="
echo "DONE!"
echo "Newman HTML reports are saved in: api-testing/reports/"
echo "k6 HTML report is saved in: api-testing/k6_concurrency_performance_report.html"
echo "======================================================="
