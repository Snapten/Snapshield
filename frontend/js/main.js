// Platform switching
const platformBtns = document.querySelectorAll('[data-platform]');
const platformContainers = document.querySelectorAll('.platform-container');

platformBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const platform = btn.dataset.platform;
        
        // Update active nav button
        platformBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Show active platform container
        platformContainers.forEach(container => {
            container.classList.remove('active');
        });
        document.getElementById(`${platform}-container`).classList.add('active');
        
        // Reset to first tab
        const tabBtns = document.querySelectorAll(`#${platform}-container .tab-btn`);
        const tabContents = document.querySelectorAll(`#${platform}-container .tab-content`);
        
        tabBtns.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));
        tabBtns[0].classList.add('active');
        tabContents[0].classList.add('active');
    });
});

// Tab switching within platforms
const tabBtns = document.querySelectorAll('.tab-btn');

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;
        const container = btn.closest('.platform-container');
        
        // Update active tab button
        container.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Show active tab content
        container.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabId).classList.add('active');
    });
});

// Discord Authentication
document.getElementById('discord-login').addEventListener('click', () => {
    // Placeholder for Discord OAuth
    const accountsList = document.getElementById('discord-accounts');
    const accountItem = document.createElement('div');
    accountItem.className = 'account-item active';
    accountItem.innerHTML = `
        <span>Your_Discord#0001 (Bot)</span>
        <button class="btn-icon" title="Make Default">⭐</button>
    `;
    accountsList.appendChild(accountItem);
});

// Twitch Authentication
document.getElementById('twitch-login-streamer').addEventListener('click', () => {
    const streamerAccount = document.getElementById('twitch-streamer-account');
    streamerAccount.innerHTML = `
        <p><strong>Channel:</strong> your_channel</p>
        <p><strong>Status:</strong> Connected</p>
        <button class="btn-danger">Disconnect</button>
    `;
});

document.getElementById('twitch-login-bot').addEventListener('click', () => {
    const botAccount = document.getElementById('twitch-bot-account');
    botAccount.innerHTML = `
        <p><strong>Account:</strong> your_bot</p>
        <p><strong>Status:</strong> Connected</p>
        <button class="btn-danger">Disconnect</button>
    `;
});

// Command Management
const commandModal = document.getElementById('command-modal');
const commandForm = document.getElementById('command-form');

document.getElementById('discord-new-command').addEventListener('click', () => {
    commandForm.dataset.platform = 'discord';
    commandModal.classList.add('active');
});

document.getElementById('twitch-new-command').addEventListener('click', () => {
    commandForm.dataset.platform = 'twitch';
    commandModal.classList.add('active');
});

document.querySelector('.close').addEventListener('click', () => {
    commandModal.classList.remove('active');
    commandForm.reset();
});

commandModal.addEventListener('click', (e) => {
    if (e.target === commandModal) {
        commandModal.classList.remove('active');
    }
});

commandForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const platform = commandForm.dataset.platform;
    const name = document.getElementById('cmd-name').value;
    const response = document.getElementById('cmd-response').value;
    const permission = document.getElementById('cmd-permission').value;
    const enabled = document.getElementById('cmd-enabled').checked;
    
    const commandsList = document.getElementById(`${platform}-commands-list`);
    const commandItem = document.createElement('div');
    commandItem.className = 'command-item';
    commandItem.innerHTML = `
        <div class="command-info">
            <div class="command-name">!${name}</div>
            <div class="command-permission">${permission}</div>
        </div>
        <div class="command-actions">
            <button class="cmd-toggle ${enabled ? 'active' : ''}" title="Toggle"></button>
            <button class="btn-icon" title="Edit">✏️</button>
            <button class="btn-icon" title="Delete">🗑️</button>
        </div>
    `;
    
    commandsList.appendChild(commandItem);
    commandModal.classList.remove('active');
    commandForm.reset();
    
    // Add event listeners to toggle
    const toggleBtn = commandItem.querySelector('.cmd-toggle');
    toggleBtn.addEventListener('click', () => {
        toggleBtn.classList.toggle('active');
    });
    
    // Delete button
    const deleteBtn = commandItem.querySelector('[title="Delete"]');
    deleteBtn.addEventListener('click', () => {
        commandItem.remove();
    });
});

// Toggle switches for moderation
const moderationToggles = document.querySelectorAll('[id$="-moderation-enabled"]');
moderatorationToggles.forEach(toggle => {
    toggle.addEventListener('change', (e) => {
        console.log(`Moderation ${e.target.checked ? 'enabled' : 'disabled'}`);
    });
});

// Sample stats initialization
function initializeStats() {
    const discordStats = document.getElementById('discord-stats');
    const twitchStats = document.getElementById('twitch-stats');
    
    const discordStatsHTML = `
        <div class="stat-card">
            <div class="stat-label">Messages Today</div>
            <div class="stat-value">0</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Moderation Actions</div>
            <div class="stat-value">0</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Custom Commands Used</div>
            <div class="stat-value">0</div>
        </div>
    `;
    
    const twitchStatsHTML = `
        <div class="stat-card">
            <div class="stat-label">Channel Follows</div>
            <div class="stat-value">0</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Moderation Actions</div>
            <div class="stat-value">0</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Commands Used</div>
            <div class="stat-value">0</div>
        </div>
    `;
    
    discordStats.innerHTML = discordStatsHTML;
    twitchStats.innerHTML = twitchStatsHTML;
}

initializeStats();

// Add some sample commands on load
function initializeSampleCommands() {
    const twitchCommandsList = document.getElementById('twitch-commands-list');
    
    const sampleCommands = [
        { name: 'uptime', permission: 'everyone', description: 'Check stream uptime' },
        { name: 'socials', permission: 'everyone', description: 'Display social links' },
        { name: 'discord', permission: 'everyone', description: 'Discord server link' },
        { name: 'lurk', permission: 'everyone', description: 'Thank user for lurking' },
        { name: 'shoutout', permission: 'mod', description: 'Give a shoutout' },
    ];
    
    sampleCommands.forEach(cmd => {
        const item = document.createElement('div');
        item.className = 'command-item';
        item.innerHTML = `
            <div class="command-info">
                <div class="command-name">!${cmd.name}</div>
                <div class="command-permission">${cmd.permission} - ${cmd.description}</div>
            </div>
            <div class="command-actions">
                <button class="cmd-toggle active" title="Toggle"></button>
                <button class="btn-icon" title="Edit">✏️</button>
                <button class="btn-icon" title="Delete">🗑️</button>
            </div>
        `;
        
        twitchCommandsList.appendChild(item);
        
        // Add event listeners
        const toggleBtn = item.querySelector('.cmd-toggle');
        toggleBtn.addEventListener('click', () => {
            toggleBtn.classList.toggle('active');
        });
        
        const deleteBtn = item.querySelector('[title="Delete"]');
        deleteBtn.addEventListener('click', () => {
            item.remove();
        });
    });
}

initializeSampleCommands();

console.log('Snapshield Dashboard initialized');
