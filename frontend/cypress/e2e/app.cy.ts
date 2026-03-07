describe("Career Copilot shell", () => {
  it("loads the workflow stages and performs auto-login request", () => {
    cy.intercept("POST", "**/auth/login", {
      statusCode: 200,
      body: { access_token: "fake-token", token_type: "bearer" },
    }).as("login");

    cy.visit("/");

    cy.wait("@login").its("response.statusCode").should("eq", 200);
    cy.contains("Career Copilot").should("be.visible");
    cy.contains("Authenticated as seeded user.").should("be.visible");
    cy.contains("User Profile").should("be.visible");
    cy.contains("LinkedIn Optimizer").should("be.visible");
    cy.contains("Job Search").should("be.visible");
    cy.contains("Job Selection").should("be.visible");
    cy.contains("Materials").should("be.visible");
  });
});
