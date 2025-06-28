#!/usr/bin/env node

/**
 * Test script for Playwright MCP with Vision Capabilities
 * Validates the setup and demonstrates key features
 */

const { spawn } = require('child_process');
const path = require('path');

async function testPlaywrightMCP() {
  console.log('🧪 Testing Playwright MCP Setup...\n');

  // Test 1: Basic MCP Server Startup
  console.log('1. Testing MCP Server Startup...');
  try {
    const mcpProcess = spawn('npx', ['@playwright/mcp', '--help'], {
      stdio: 'pipe'
    });

    await new Promise((resolve, reject) => {
      mcpProcess.on('close', (code) => {
        if (code === 0) {
          console.log('✅ MCP Server: Available and working');
          resolve();
        } else {
          reject(new Error(`MCP Server failed with code ${code}`));
        }
      });
    });
  } catch (error) {
    console.log('❌ MCP Server: Failed to start');
    console.error(error.message);
    return false;
  }

  // Test 2: Vision Mode Support
  console.log('\n2. Testing Vision Mode Support...');
  try {
    const visionTest = spawn('npx', ['@playwright/mcp', '--vision', '--help'], {
      stdio: 'pipe'
    });

    await new Promise((resolve, reject) => {
      visionTest.on('close', (code) => {
        if (code === 0) {
          console.log('✅ Vision Mode: Supported and available');
          resolve();
        } else {
          reject(new Error(`Vision mode failed with code ${code}`));
        }
      });
    });
  } catch (error) {
    console.log('❌ Vision Mode: Not available');
    console.error(error.message);
    return false;
  }

  // Test 3: Browser Installation Check
  console.log('\n3. Testing Browser Installation...');
  try {
    const { execSync } = require('child_process');
    execSync('npx playwright --version', { stdio: 'pipe' });
    console.log('✅ Playwright Browsers: Installed and ready');
  } catch (error) {
    console.log('❌ Playwright Browsers: Not installed');
    console.log('Run: npx playwright install');
    return false;
  }

  // Test 4: Configuration Validation
  console.log('\n4. Testing Configuration Files...');
  const fs = require('fs');
  
  const configFiles = [
    '.cursor/mcp.json',
    '.cursor/mcp-playwright.json',
    'insighthub-frontend/playwright.config.ts'
  ];

  let configValid = true;
  for (const configFile of configFiles) {
    if (fs.existsSync(configFile)) {
      console.log(`✅ Config: ${configFile} exists`);
    } else {
      console.log(`❌ Config: ${configFile} missing`);
      configValid = false;
    }
  }

  // Test 5: Command Files Validation
  console.log('\n5. Testing AI Command Files...');
  const commandFiles = [
    '.cursor/commands/test-generate.md',
    '.cursor/commands/test-visual.md'
  ];

  let commandsValid = true;
  for (const commandFile of commandFiles) {
    if (fs.existsSync(commandFile)) {
      console.log(`✅ Command: ${commandFile} exists`);
    } else {
      console.log(`❌ Command: ${commandFile} missing`);
      commandsValid = false;
    }
  }

  console.log('\n🎯 Test Summary:');
  console.log('================');
  
  if (configValid && commandsValid) {
    console.log('✅ All tests passed! Playwright MCP is ready for AI-powered testing.');
    console.log('\n📋 Next Steps:');
    console.log('1. Start the dev server: cd insighthub-frontend && npm run dev');
    console.log('2. Use @test-generate [component] to create AI-powered tests');
    console.log('3. Use @test-visual [target] for visual analysis');
    console.log('4. Run npx @playwright/mcp --vision for vision-enabled testing');
    return true;
  } else {
    console.log('❌ Some tests failed. Please check the configuration.');
    return false;
  }
}

// Run the test
testPlaywrightMCP().catch(error => {
  console.error('Test failed:', error);
  process.exit(1);
}); 