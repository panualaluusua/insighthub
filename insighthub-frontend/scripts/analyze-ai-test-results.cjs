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
  
  console.log('\n🤖 Enhanced Playwright MCP - AI Testing Analysis Report');
  console.log('=' .repeat(60));
  
  if (!fs.existsSync(resultsDir)) {
    console.log('\n❌ No AI test results found.');
    console.log('💡 Run AI tests first: npm run test:ai');
    return;
  }
  
  try {
    const files = fs.readdirSync(resultsDir);
    
    // Categorize files
    const screenshots = files.filter(f => f.endsWith('.png'));
    const reports = files.filter(f => f.endsWith('.md'));
    const jsonReports = files.filter(f => f.endsWith('.json'));
    const accessibilityReports = files.filter(f => f.includes('accessibility'));
    const performanceReports = files.filter(f => f.includes('performance'));
    const bugReports = files.filter(f => f.includes('bug-detection'));
    
    // Summary statistics
    console.log(`\n📊 Test Results Summary:`);
    console.log(`   📷 Screenshots captured: ${screenshots.length}`);
    console.log(`   📋 Reports generated: ${reports.length}`);
    console.log(`   🔍 JSON analysis files: ${jsonReports.length}`);
    console.log(`   ♿ Accessibility reports: ${accessibilityReports.length}`);
    console.log(`   ⚡ Performance reports: ${performanceReports.length}`);
    console.log(`   🐛 Bug detection reports: ${bugReports.length}`);
    
    // Visual evidence analysis
    if (screenshots.length > 0) {
      console.log(`\n📷 Visual Evidence Captured:`);
      
      const categorizedScreenshots = {
        responsive: screenshots.filter(s => s.includes('responsive')),
        components: screenshots.filter(s => s.includes('component')),
        forms: screenshots.filter(s => s.includes('form') || s.includes('signin') || s.includes('signup')),
        navigation: screenshots.filter(s => s.includes('nav')),
        other: screenshots.filter(s => 
          !s.includes('responsive') && 
          !s.includes('component') && 
          !s.includes('form') && 
          !s.includes('signin') && 
          !s.includes('signup') && 
          !s.includes('nav')
        )
      };
      
      Object.entries(categorizedScreenshots).forEach(([category, files]) => {
        if (files.length > 0) {
          console.log(`   🎯 ${category.charAt(0).toUpperCase() + category.slice(1)}: ${files.length} images`);
          files.forEach(file => console.log(`      - ${file}`));
        }
      });
    }
    
    // Bug detection analysis
    if (bugReports.length > 0) {
      console.log(`\n🐛 Bug Detection Analysis:`);
      bugReports.forEach(report => {
        try {
          const reportPath = path.join(resultsDir, report);
          const content = fs.readFileSync(reportPath, 'utf8');
          
          // Extract key findings (simple text analysis)
          const lines = content.split('\n');
          const criticalIssues = lines.filter(line => 
            line.toLowerCase().includes('critical') || 
            line.toLowerCase().includes('failed') ||
            line.toLowerCase().includes('error')
          );
          
          console.log(`   📄 ${report}:`);
          if (criticalIssues.length > 0) {
            console.log(`      ⚠️ Critical issues found: ${criticalIssues.length}`);
            criticalIssues.slice(0, 3).forEach(issue => {
              console.log(`         • ${issue.trim()}`);
            });
            if (criticalIssues.length > 3) {
              console.log(`         ... and ${criticalIssues.length - 3} more`);
            }
          } else {
            console.log(`      ✅ No critical issues detected`);
          }
        } catch (error) {
          console.log(`      ❌ Error reading report: ${error.message}`);
        }
      });
    }
    
    // Accessibility analysis
    if (accessibilityReports.length > 0) {
      console.log(`\n♿ Accessibility Analysis:`);
      accessibilityReports.forEach(report => {
        console.log(`   📄 ${report}`);
        try {
          const reportPath = path.join(resultsDir, report);
          const content = fs.readFileSync(reportPath, 'utf8');
          
          if (report.endsWith('.json')) {
            const data = JSON.parse(content);
            if (data.violations && data.violations.length > 0) {
              console.log(`      ⚠️ WCAG violations found: ${data.violations.length}`);
              data.violations.slice(0, 3).forEach(violation => {
                console.log(`         • ${violation.id}: ${violation.description}`);
              });
            } else {
              console.log(`      ✅ No accessibility violations detected`);
            }
          }
        } catch (error) {
          console.log(`      ❌ Error analyzing accessibility report: ${error.message}`);
        }
      });
    }
    
    // Performance analysis
    if (performanceReports.length > 0) {
      console.log(`\n⚡ Performance Analysis:`);
      performanceReports.forEach(report => {
        console.log(`   📄 ${report}`);
        try {
          const reportPath = path.join(resultsDir, report);
          const content = fs.readFileSync(reportPath, 'utf8');
          
          // Look for performance metrics in the content
          const lines = content.split('\n');
          const perfMetrics = lines.filter(line => 
            line.includes('ms') || 
            line.includes('load') || 
            line.includes('performance') ||
            line.toLowerCase().includes('lcp') ||
            line.toLowerCase().includes('fid') ||
            line.toLowerCase().includes('cls')
          );
          
          if (perfMetrics.length > 0) {
            console.log(`      📈 Performance metrics detected:`);
            perfMetrics.slice(0, 3).forEach(metric => {
              console.log(`         • ${metric.trim()}`);
            });
          }
        } catch (error) {
          console.log(`      ❌ Error analyzing performance report: ${error.message}`);
        }
      });
    }
    
    // Recommendations
    console.log(`\n💡 AI-Powered Recommendations:`);
    
    if (bugReports.length === 0) {
      console.log(`   🎯 Run bug detection: npm run test:bug-detection`);
    }
    
    if (screenshots.length < 5) {
      console.log(`   📷 Increase visual coverage by testing more components`);
    }
    
    if (accessibilityReports.length === 0) {
      console.log(`   ♿ Run accessibility analysis: npm run test:a11y`);
    }
    
    console.log(`   🔍 View detailed reports: npx playwright show-report`);
    console.log(`   📊 Generate new analysis: npm run test:ai`);
    
    // Next steps
    console.log(`\n🚀 Next Steps:`);
    console.log(`   1. Review any critical issues identified above`);
    console.log(`   2. Check individual screenshot files for visual validation`);
    console.log(`   3. Address accessibility violations if found`);
    console.log(`   4. Implement performance optimizations if needed`);
    console.log(`   5. Re-run AI tests after fixes: npm run test:ai`);
    
    console.log('\n' + '='.repeat(60));
    console.log('✨ AI Testing Analysis Complete');
    
  } catch (error) {
    console.error('\n❌ Error analyzing AI test results:', error.message);
    console.log('\n💡 Try running AI tests first: npm run test:ai');
  }
}

// Run the analysis
analyzeAITestResults(); 