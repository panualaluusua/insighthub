#!/usr/bin/env node

/**
 * AI Test Results Analyzer
 * 
 * This script analyzes the results from our Enhanced Playwright MCP Testing system
 * and provides actionable insights from AI-powered testing.
 */

const fs = require('fs');
const path = require('path');

function analyzeAITestResults() {
  const resultsDir = path.join(__dirname, '../test-results/ai-analysis');
  
  console.log('\\n🤖 Enhanced Playwright MCP - AI Testing Analysis Report');
  console.log('=' .repeat(60));
  
  if (!fs.existsSync(resultsDir)) {
    console.log('\\n❌ No AI test results found.');
    console.log('💡 Run AI tests first: npm run test:ai');
    return;
  }
  
  try {
    const files = fs.readdirSync(resultsDir);
    
    // Categorize files
    const screenshots = files.filter(f => f.endsWith('.png'));
    const reports = files.filter(f => f.endsWith('.md'));
    const jsonReports = files.filter(f => f.endsWith('.json'));
    
    // Summary statistics
    console.log(`\\n📊 Test Results Summary:`);
    console.log(`   📷 Screenshots captured: ${screenshots.length}`);
    console.log(`   📋 Reports generated: ${reports.length}`);
    console.log(`   🔍 JSON analysis files: ${jsonReports.length}`);
    
    // Visual evidence analysis
    if (screenshots.length > 0) {
      console.log(`\\n📷 Visual Evidence Captured:`);
      screenshots.forEach(screenshot => {
        console.log(`   - ${screenshot}`);
      });
    }
    
    // Bug detection analysis
    if (reports.length > 0) {
      console.log(`\\n📋 AI Reports Generated:`);
      reports.forEach(report => {
        console.log(`   - ${report}`);
      });
    }
    
    // Recommendations
    console.log(`\\n💡 AI-Powered Recommendations:`);
    console.log(`   🔍 View detailed reports: npx playwright show-report`);
    console.log(`   📊 Generate new analysis: npm run test:ai`);
    
    console.log('\\n' + '='.repeat(60));
    console.log('✨ AI Testing Analysis Complete');
    
  } catch (error) {
    console.error('\\n❌ Error analyzing AI test results:', error.message);
    console.log('\\n💡 Try running AI tests first: npm run test:ai');
  }
}

// Run the analysis
analyzeAITestResults(); 