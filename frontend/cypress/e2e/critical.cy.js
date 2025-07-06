describe('Критические e2e-тесты CRM', () => {
  it('Должен открыть главную страницу', () => {
    cy.visit('/');
    cy.contains('Главная').should('exist');
  });

  it('Должен показать форму логина при разлогине', () => {
    cy.visit('/logout');
    cy.url().should('include', '/login');
    cy.get('input[type="text"]').should('exist');
    cy.get('input[type="password"]').should('exist');
  });

  it('Должен залогиниться и увидеть меню', () => {
    cy.visit('/login');
    cy.get('input[type="text"]').type('demo');
    cy.get('input[type="password"]').type('demo123');
    cy.get('button[type="submit"]').click();
    cy.contains('Главная').should('exist');
    cy.get('aside').should('exist');
  });
}); 