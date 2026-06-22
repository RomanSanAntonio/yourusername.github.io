const socket = io();
let companies = {};

async function load() {
    const res = await fetch("/api/companies");
    const data = await res.json();
    companies = Object.fromEntries(data.map(c => [c.id, c]));
    render();
}

socket.on("update", (data) => {
    companies = data;
    render();
});

function trade(id, action) {
    const user = document.getElementById("user").value || "anon";
    const amount = prompt("amount?");

    fetch("/api/trade", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            user,
            company_id: id,
            action,
            amount: parseInt(amount)
        })
    });
}

function render() {
    const list = document.getElementById("list");
    list.innerHTML = "";

    Object.values(companies).forEach(c => {
        list.innerHTML += `
            <div class="card">
                <h2>${c.name} (${c.ticker})</h2>
                <div class="price">$${c.price.toFixed(2)}</div>
                <div>Available: ${c.available}/${c.max_shares}</div>

                <button onclick="trade(${c.id}, 'buy')">Buy</button>
                <button onclick="trade(${c.id}, 'sell')">Sell</button>
            </div>
        `;
    });
}

load();
