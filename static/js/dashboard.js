
/* ============================================================
   CAAI Dashboard — Frontend Interactions
   Sidebar, notifications, dark mode, stats, tax gauge,
   and floating AI Assistant connected to the Flask backend.
============================================================ */

document.addEventListener("DOMContentLoaded", () => {
  "use strict";

  /* ---------- Sidebar collapse (desktop) ---------- */
  const sidebar = document.getElementById("sidebar");
  const sidebarToggle = document.getElementById("sidebarToggle");

  if (sidebar && sidebarToggle) {
    sidebarToggle.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
    });
  }

  /* ---------- Mobile sidebar ---------- */
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");

  if (sidebar && mobileMenuBtn) {
    mobileMenuBtn.addEventListener("click", () => {
      sidebar.classList.toggle("mobile-open");
    });
  }

  document.querySelectorAll(".nav-item").forEach((link) => {
    link.addEventListener("click", () => {
      if (sidebar && window.innerWidth <= 720) {
        sidebar.classList.remove("mobile-open");
      }
    });
  });

  /* ---------- Notification dropdown ---------- */
  const notifBtn = document.getElementById("notifBtn");
  const notifDropdown = document.getElementById("notifDropdown");

  if (notifBtn && notifDropdown) {
    notifBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      notifDropdown.classList.toggle("open");
    });

    notifDropdown.addEventListener("click", (event) => {
      event.stopPropagation();
    });

    document.addEventListener("click", () => {
      notifDropdown.classList.remove("open");
    });
  }

  /* ---------- Dark mode ---------- */
  const darkModeBtn = document.getElementById("darkModeBtn");

  if (darkModeBtn) {
    darkModeBtn.addEventListener("click", () => {
      document.body.classList.toggle("dark");
    });
  }

  /* ---------- Animated statistic counters ---------- */
  document.querySelectorAll(".stat-value[data-count]").forEach((element) => {
    const target = Number.parseInt(element.dataset.count, 10) || 0;
    const prefix = element.dataset.prefix || "";
    const duration = 900;
    const startTime = performance.now();

    function animateCounter(now) {
      const progress = Math.min((now - startTime) / duration, 1);
      const easedProgress = 1 - Math.pow(1 - progress, 3);
      const value = Math.round(easedProgress * target);

      element.textContent = prefix + value.toLocaleString("en-IN");

      if (progress < 1) {
        requestAnimationFrame(animateCounter);
      }
    }

    requestAnimationFrame(animateCounter);
  });

  /* ---------- Tax efficiency gauge ---------- */
  const gaugeCircle = document.getElementById("gaugeCircle");
  const gaugeNumber = document.getElementById("gaugeNumber");

  if (gaugeCircle && gaugeNumber) {
    // Placeholder only. Replace with the real backend score when available.
    const score = 42;
    const radius = 52;
    const circumference = 2 * Math.PI * radius;
    const targetOffset = circumference * (1 - score / 100);

    gaugeCircle.style.strokeDasharray = String(circumference);
    gaugeCircle.style.strokeDashoffset = String(circumference);

    const startTime = performance.now();
    const duration = 1100;

    function animateGauge(now) {
      const progress = Math.min((now - startTime) / duration, 1);
      const easedProgress = 1 - Math.pow(1 - progress, 3);

      gaugeCircle.style.strokeDashoffset = String(
        circumference - easedProgress * (score / 100) * circumference
      );

      gaugeNumber.textContent = String(Math.round(easedProgress * score));

      if (progress < 1) {
        requestAnimationFrame(animateGauge);
      } else {
        gaugeCircle.style.strokeDashoffset = String(targetOffset);
      }
    }

    requestAnimationFrame(animateGauge);
  }

  /* ============================================================
     FLOATING AI TAX ASSISTANT
  ============================================================ */

  const aiFab = document.getElementById("aiFab");
  const aiChatWindow = document.getElementById("aiChatWindow");
  const closeChat = document.getElementById("closeChat");
  const chatInput = document.getElementById("chatInput");
  const sendButton = document.getElementById("sendMessage");
  const chatMessages = document.getElementById("chatMessages");
  const promptButtons = document.querySelectorAll(".prompt-btn");
  const sidebarAI = document.getElementById("sidebarAiAssistant");
  const quickAI = document.getElementById("quickAiAssistant");

  // Prefer the Flask-generated URL from the dashboard template.
  // "/chat" is the fallback for the current app's route configuration.
  const chatEndpoint =
    aiChatWindow?.dataset.chatUrl || "/chat";

  let chatSending = false;

  /* ---------- Open assistant ---------- */
  function openAI() {
    if (!aiChatWindow) return;

    aiChatWindow.classList.add("show");
    aiChatWindow.setAttribute("aria-hidden", "false");

    if (aiFab) {
      aiFab.style.display = "none";
    }

    if (chatInput && !chatSending) {
      chatInput.focus();
    }
  }

  /* ---------- Close assistant ---------- */
  function closeAI() {
    if (!aiChatWindow) return;

    aiChatWindow.classList.remove("show");
    aiChatWindow.setAttribute("aria-hidden", "true");

    if (aiFab) {
      aiFab.style.display = "";
    }
  }

  /* ---------- Floating button ---------- */
  if (aiFab) {
    aiFab.addEventListener("click", () => {
      if (aiChatWindow?.classList.contains("show")) {
        closeAI();
      } else {
        openAI();
      }
    });
  }

  /* ---------- Close button ---------- */
  if (closeChat) {
    closeChat.addEventListener("click", closeAI);
  }

  /* ---------- Sidebar assistant link ---------- */
  if (sidebarAI) {
    sidebarAI.addEventListener("click", (event) => {
      event.preventDefault();
      openAI();
    });
  }

  /* ---------- Quick action assistant link ---------- */
  if (quickAI) {
    quickAI.addEventListener("click", (event) => {
      event.preventDefault();
      openAI();
    });
  }

  /* ---------- Escape key ---------- */
  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Escape" &&
      aiChatWindow?.classList.contains("show")
    ) {
      closeAI();
    }
  });

  /* ---------- Add a chat message safely ---------- */
  function addMessage(text, sender) {
    if (!chatMessages) return null;

    const message = document.createElement("div");

    message.className = sender;
    message.style.margin = "12px 0";
    message.style.padding = "12px 15px";
    message.style.borderRadius = "14px";
    message.style.maxWidth = "85%";
    message.style.whiteSpace = "pre-wrap";
    message.style.overflowWrap = "anywhere";
    message.style.lineHeight = "1.5";

    // Use textContent to prevent responses from being treated as HTML.
    message.textContent = String(text ?? "");

    if (sender === "user") {
      message.style.marginLeft = "auto";
      message.style.background = "#4f7cff";
      message.style.color = "#ffffff";
    } else {
      message.style.marginRight = "auto";
      message.style.background = "#eef2ff";
      message.style.color = "#222222";
    }

    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return message;
  }

  /* ---------- Send a question to Flask ---------- */
  async function sendQuestion(question) {
    const cleanedQuestion = String(question ?? "").trim();

    if (!cleanedQuestion || chatSending) return;

    if (!chatMessages) {
      console.error("CAAI: Chat message container was not found.");
      return;
    }

    chatSending = true;

    if (sendButton) sendButton.disabled = true;
    if (chatInput) chatInput.disabled = true;

    openAI();
    addMessage(cleanedQuestion, "user");

    if (chatInput) {
      chatInput.value = "";
    }

    const loadingMessage = addMessage("Thinking...", "bot");

    try {
      const response = await fetch(chatEndpoint, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json"
        },
        body: JSON.stringify({
          question: cleanedQuestion
        })
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          throw new Error(
            "Your session may have expired. Please log in again."
          );
        }

        if (
          response.status === 503 ||
          String(data.error || "").includes("503 UNAVAILABLE") ||
          String(data.error || "").toLowerCase().includes("high demand")
        ) {
          throw new Error(
            "The AI service is temporarily busy. Please try again shortly."
          );
        }

        throw new Error(
          data.error || `The request failed (HTTP ${response.status}).`
        );
      }

      if (typeof data.answer !== "string" || !data.answer.trim()) {
        throw new Error("The assistant returned an empty response.");
      }

      if (loadingMessage) {
        loadingMessage.textContent = data.answer;
      }
    } catch (error) {
      console.error("CAAI chatbot request failed:", error);

      if (loadingMessage) {
        if (error instanceof TypeError) {
          loadingMessage.textContent =
            "Unable to reach the assistant. Check your connection and try again.";
        } else {
          loadingMessage.textContent =
            error.message || "Something went wrong. Please try again.";
        }
      }
    } finally {
      chatSending = false;

      if (sendButton) sendButton.disabled = false;

      if (chatInput) {
        chatInput.disabled = false;

        if (aiChatWindow?.classList.contains("show")) {
          chatInput.focus();
        }
      }
    }
  }

  /* ---------- Send button ---------- */
  if (sendButton && chatInput) {
    sendButton.addEventListener("click", () => {
      sendQuestion(chatInput.value);
    });

    // Enter sends. Shift+Enter can be used for a new line where supported.
    chatInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendQuestion(chatInput.value);
      }
    });
  }

  /* ---------- Suggested question buttons ---------- */
  promptButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const question = button.textContent.trim();

      if (question) {
        sendQuestion(question);
      }
    });
  });

});
