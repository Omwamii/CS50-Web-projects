document.addEventListener("DOMContentLoaded", function () {
  // Use buttons to toggle between views
  document
    .querySelector("#inbox")
    .addEventListener("click", () => load_mailbox("inbox"));
  document
    .querySelector("#sent")
    .addEventListener("click", () => load_mailbox("sent"));
  document
    .querySelector("#archived")
    .addEventListener("click", () => load_mailbox("archive"));
  document.querySelector("#compose").addEventListener("click", compose_email);

  // By default, load the inbox
  load_mailbox("inbox");
});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#email-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";

  // Clear out composition fields
  document.querySelector("#compose-recipients").value = "";
  document.querySelector("#compose-subject").value = "";
  document.querySelector("#compose-body").value = "";

  form = document.getElementById("compose-form");
  form.addEventListener("submit", () => {
    // make a post request to send email
    const mailRecipients = document.getElementById("compose-recipients").value;
    const mailSubject = document.getElementById("compose-subject").value;
    const mailBody = document.getElementById("compose-body").value;

    fetch("/emails", {
      method: "POST",
      body: JSON.stringify({
        recipients: mailRecipients, // list of recipients
        subject: mailSubject,
        body: mailBody,
      }),
    })
      .then((result) => {
        // Print result
        console.log("Success");
        console.log(result.status);
        if (result.status === 201) {
          console.log("Mail sent successfully");
        }
      })
      .catch((error) => {
        console.error(error);
        alert(error);
      });
  });
}

async function updateRead(mailId, flag) {
  return new Promise((resolve, reject) => {
    // handle marking as read / unread

    fetch(`/emails/${mailId}`)
      .then((res) => res.json())
      .then(() => {
        // since the user clicked, mark the mail as read
        fetch(`/emails/${mailId}`, {
          method: "PUT",
          body: JSON.stringify({
            read: flag,
          }),
        })
          .then((result) => {
            console.log("Updating read status...");
            console.log(result.status);
            resolve();
          })
          .catch((error) => {
            console.error(error);
            reject(error);
          });
      });
  });
}

async function updateArchive(mailId, flag) {
  return new Promise((resolve, reject) => {
    // handle marking as read / unread

    fetch(`/emails/${mailId}`)
      .then((res) => res.json())
      .then(() => {
        fetch(`/emails/${mailId}`, {
          method: "PUT",
          body: JSON.stringify({
            archived: flag,
          }),
        })
          .then((result) => {
            console.log("Updating archived status...");
            console.log(result.status);
            resolve();
          })
          .catch((error) => {
            console.error(error);
            reject(error);
          });
      });
  });
}

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector("#emails-view").style.display = "block";
  document.querySelector("#email-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "none";

  // Show the mailbox name
  document.querySelector("#emails-view").innerHTML = `<h3>${
    mailbox.charAt(0).toUpperCase() + mailbox.slice(1)
  }</h3>`;
  document.querySelector("#emails-view").classList.add("b-text");

  // fetch all emails & display depending on type of inbox
  fetch(`/emails/${mailbox}`)
    .then((response) => response.json())
    .then((data) => {
      const mails = document.querySelector("#emails-view");
      const container = document.createElement("div");

      for (const mail of data) {
        const el = document.createElement("div");

        const sender = document.createElement("span");
        const sub = document.createElement("span");

        if (mailbox === "sent") {
          // put recipient instead of sender
          sender.innerHTML = `To: ${mail.recipients}`;
        } else {
          sender.innerHTML = mail.sender;
        }

        sub.innerHTML = mail.subject;

        el.append(sender, sub);
        el.dataset.id = mail.id;
        el.classList.add("mail");

        if (mailbox === "inbox") {
          // add google material icon for archiving message before view
          const archIcon = document.createElement("span");
          archIcon.classList.add("material-symbols-outlined");
          if (mail.archived) {
            archIcon.innerHTML = "unarchive";
            archIcon.setAttribute("title", "Unarchive");
          } else {
            archIcon.innerHTML = "archive";
            archIcon.setAttribute("title", "Archive");
          }

          archIcon.addEventListener("click", async (event) => {
            event.stopPropagation();
            const flag = mail.archived ? false : true;

            try {
              // force wait for all async ops tp finish
              await updateArchive(mail.id, flag);

              // Only reload after all async operations done
              window.location.reload(true);
            } catch (error) {
              console.error("Error:", error);
            }
          });

          const readIcon = document.createElement("span");
          readIcon.classList.add("material-symbols-outlined");
          if (mail.read) {
            readIcon.innerHTML = "mark_as_unread";
            readIcon.setAttribute("title", "Mark as unread");
          } else {
            readIcon.innerHTML = "mark_chat_read";
            readIcon.setAttribute("title", "Mark as read");
          }

          readIcon.addEventListener("click", async (event) => {
            event.stopPropagation();
            const flag = mail.read ? false : true;

            try {
              // force wait for all async ops tp finish
              await updateRead(mail.id, flag);

              // Only reload after all async operations done
              window.location.reload(true);
            } catch (error) {
              console.error("Error:", error);
            }
          });

          el.append(readIcon, archIcon);
        } else if (mailbox === "archive") {
          const archIcon = document.createElement("span"); 
          archIcon.classList.add("material-symbols-outlined"); // Add a class to the element
          if (mail.archived) {
            archIcon.innerHTML = "unarchive";
            archIcon.setAttribute("title", "Unarchive");
          } else {
            archIcon.innerHTML = "archive";
            archIcon.setAttribute("title", "Archive");
          }

          archIcon.addEventListener("click", async (event) => {
            event.stopPropagation();
            const flag = mail.archived ? false : true;

            try {
              // force wait for all async ops tp finish
              await updateArchive(mail.id, flag);

              // Only reload after all async operations done
              window.location.reload(true);
            } catch (error) {
              console.error("Error:", error);
            }
          });
          el.append(archIcon);
        }
        const time = document.createElement("span");
        time.innerHTML = mail.timestamp;
        el.append(time);

        el.addEventListener("click", () => {
          // fetch specific email with data-set id

          document.querySelector("#emails-view").style.display = "none";
          const msg = document.querySelector("#email-view");
          const mailSub = document.createElement("h2");
          const recipients = document.createElement("h3");
          const sender = document.createElement("h3");
          const time = document.createElement("h3");
          const replyBtn = document.createElement("button");
          const archBtn = document.createElement("button");
          const body = document.createElement("p");
          msg.style.display = "block";
          msg.style.color = "white";
          msg.innerHTML = "";

          fetch(`/emails/${el.dataset.id}`)
            .then((res) => res.json())
            .then((data) => {
              sender.innerHTML = `From: ${data.sender}`;
              mailSub.innerHTML = `Subject: ${data.subject}`;
              recipients.innerHTML = `To: ${data.recipients}`;
              time.innerHTML = `Time: ${data.timestamp}`;

              if (mail.archived) {
                archBtn.innerHTML = "Unarchive";
              } else {
                archBtn.innerHTML = "Archive";
              }
              archBtn.classList.add("reply-btn");
              archBtn.addEventListener("click", async () => {
                try {
                  // force wait for all async ops tp finish
                  await updateArchive(mail.id, mail.archived ? false : true);

                  // Only reload after all async operations done
                  window.location.reload(true);
                } catch (error) {
                  console.error("Error:", error);
                }
              });

              replyBtn.innerHTML = "Reply";
              replyBtn.classList.add("reply-btn");
              replyBtn.addEventListener("click", () => {
                // handle replying to mail

                document.querySelector("#emails-view").style.display = "none";
                document.querySelector("#email-view").style.display = "none";
                document.querySelector("#compose-view").style.display = "block";

                // Clear out composition fields
                document.querySelector(
                  "#compose-recipients"
                ).value = `${mail.sender}`;
                if (mail.subject.startsWith("RE: ")) {
                  document.querySelector("#compose-subject").value =
                    mail.subject;
                } else {
                  document.querySelector(
                    "#compose-subject"
                  ).value = `RE: ${mail.subject}`;
                }
                if (mail.subject.startd);
                const pre =
                  "------------------------------------------------------------------------------";
                document.querySelector(
                  "#compose-body"
                ).value = `\n${pre}\nOn ${mail.timestamp} ${mail.sender} wrote:\n ${mail.body}`;

                form = document.getElementById("compose-form");
                form.addEventListener("submit", () => {
                  // make a post request to reply to email
                  const mailRecipients =
                    document.getElementById("compose-recipients").value;
                  const mailSubject =
                    document.getElementById("compose-subject").value;
                  const mailBody =
                    document.getElementById("compose-body").value;
                  // mailBody.setAttribute('autofocus', 'true');

                  fetch("/emails", {
                    method: "POST",
                    body: JSON.stringify({
                      recipients: mailRecipients, // list of recipients
                      subject: mailSubject,
                      body: mailBody,
                    }),
                  })
                    .then((result) => {
                      // Print result
                      console.log("Success");
                      console.log(result.status);
                      if (result.status === 201) {
                        console.log("Mail sent successfully");
                      }
                    })
                    .catch((error) => {
                      console.error(error);
                      alert(error);
                    });
                });
              });

              body.innerHTML = data.body;

              msg.append(
                mailSub,
                sender,
                recipients,
                time,
                body,
                replyBtn,
                archBtn
              );
              if (!data.read) {
                updateRead(data.id, true);
              }
            })
            .catch((error) => console.error(error));
        });

        if (mail.read) {
          el.classList.add("read");
        } else {
          el.classList.add("unread");
        }
        container.appendChild(el);
      }
      mails.appendChild(container);
    })
    .catch((error) => console.error(error));
}
