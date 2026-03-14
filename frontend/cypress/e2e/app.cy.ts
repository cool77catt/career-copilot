describe("Career Copilot shell", () => {
  const stubAuthAndProfile = () => {
    cy.intercept("POST", "**/auth/login", {
      statusCode: 200,
      body: { access_token: "fake-token", token_type: "bearer" },
    }).as("login");
    cy.intercept("GET", "**/profile", {
      statusCode: 200,
      body: {
        profile_markdown_path: "/tmp/profile.md",
        section_markdown_paths: {},
        profile_report_latest_path: null,
        profile_report_revision_paths: [],
        content: "",
        follow_up_questions: [],
        follow_up_answers: {},
        additional_information: "",
        has_linkedin_profile: false,
        has_resume: false,
        updated_at: null,
      },
    }).as("profile");
  };

  it("loads the workflow stages and performs auto-login request", () => {
    stubAuthAndProfile();

    cy.visit("/");

    cy.wait("@login").its("response.statusCode").should("eq", 200);
    cy.wait("@profile").its("response.statusCode").should("eq", 200);
    cy.contains("Career Copilot").should("be.visible");
    cy.contains("Authenticated as seeded user.").should("be.visible");
    cy.contains("Profiles").should("be.visible");
    cy.contains("User Profile").should("be.visible");
    cy.contains("LinkedIn Optimizer").should("be.visible");
    cy.contains("Job Search").should("be.visible");
    cy.contains("Job Selection").should("be.visible");
    cy.contains("Materials").should("be.visible");
  });

  it("navigates to profiles and renders both top-level sections", () => {
    stubAuthAndProfile();

    cy.visit("/");
    cy.wait("@login").its("response.statusCode").should("eq", 200);
    cy.wait("@profile").its("response.statusCode").should("eq", 200);

    cy.get("aside").contains("Profiles").click();
    cy.url().should("include", "/profiles");
    cy.contains("User Information").should("be.visible");
    cy.contains("Job-Specific Profiles").should("be.visible");
    cy.contains("1. LinkedIn Profile Input").should("be.visible");
    cy.contains("2. Resume Input").should("be.visible");
    cy.contains("3. Follow-up Questions and Answers").should("be.visible");
    cy.contains("4. Additional Information").should("be.visible");
    cy.contains("button", "Update Profile").should("be.visible");
  });

  it("renders profiles submenu entries and opens url-backed profile pages", () => {
    stubAuthAndProfile();

    cy.visit("/profiles", {
      onBeforeLoad: (win) => {
        win.localStorage.setItem(
          "career_copilot_job_profiles",
          JSON.stringify([
            {
              id: "senior-software-engineer",
              name: "Senior Software Engineer",
              updatedAt: "2026-03-14T11:00:00.000Z",
            },
          ]),
        );
      },
    });

    cy.wait("@login").its("response.statusCode").should("eq", 200);
    cy.wait("@profile").its("response.statusCode").should("eq", 200);

    cy.get("aside").contains("Overview").should("be.visible");
    cy.get("aside").contains("Senior Software Engineer").should("be.visible");

    cy.contains("td", "Senior Software Engineer").click();
    cy.url().should("include", "/profiles/senior-software-engineer");
    cy.contains("Senior Software Engineer").should("be.visible");
  });
});
