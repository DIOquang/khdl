const container = document.querySelector(".container");
const demoBtn = document.querySelector(".navigation a:nth-child(3)");
const homeBtn = document.querySelector(".navigation a:nth-child(2)");
const form = document.getElementById("summary-form");
const fileInput = document.getElementById("file-input");
const modelInput = document.getElementById("model-input");
const runBtn = document.getElementById("run-btn");
const resetBtn = document.getElementById("reset-btn");
const statusText = document.getElementById("status-text");
const tableBody = document.querySelector("#result-table tbody");

demoBtn.addEventListener("click", (e) => {
  e.preventDefault();
  container.classList.add("change");
});

homeBtn.addEventListener("click", (e) => {
  e.preventDefault();
  container.classList.remove("change");
});

resetBtn.addEventListener("click", () => {
  fileInput.value = "";
  modelInput.value = "llama-3.1-8b-instant";
  tableBody.innerHTML = "";
  statusText.textContent = "Da reset. San sang.";
});

function renderRows(rows) {
  tableBody.innerHTML = "";
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    const tdCluster = document.createElement("td");
    const tdSummary = document.createElement("td");
    tdCluster.textContent = row.cluster || "";
    tdSummary.textContent = row.tom_tat || "";
    tr.appendChild(tdCluster);
    tr.appendChild(tdSummary);
    tableBody.appendChild(tr);
  });
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = fileInput.files[0];
  if (!file) {
    statusText.textContent = "Ban can chon file .xlsx truoc.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("model", modelInput.value.trim() || "llama-3.1-8b-instant");

  runBtn.disabled = true;
  statusText.textContent = "Dang phan tich cluster...";

  try {
    const res = await fetch("/api/summarize", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || "Khong the tom tat du lieu.");
    }

    renderRows(data.rows || []);
    statusText.textContent = `Hoan tat: ${data.rows?.length || 0} cluster.`;
    container.classList.add("change");
  } catch (err) {
    statusText.textContent = `Loi: ${err.message}`;
  } finally {
    runBtn.disabled = false;
  }
});
