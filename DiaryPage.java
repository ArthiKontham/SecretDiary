import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Date;

public class DiaryPage {
    private JFrame frame;
    private JTextArea diaryTextArea;
    private JTextField calcInput;
    private JLabel calcResult;
    private JTextField reminderDate;
    private JTextField reminderTime;
    private JLabel reminderMessage;

    public static void main(String[] args) {
        SwingUtilities.invokeLater(DiaryPage::new);
    }

    public DiaryPage() {
        frame = new JFrame("Daily Diary Entry");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(600, 700);
        frame.setLocationRelativeTo(null);

        frame.getContentPane().setBackground(new Color(245, 245, 220));
        frame.setLayout(new BorderLayout());

        JPanel container = new JPanel();
        container.setLayout(new BoxLayout(container, BoxLayout.Y_AXIS));
        container.setBackground(new Color(245, 245, 220));
        container.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JLabel titleLabel = new JLabel("Daily Diary Entry", JLabel.CENTER);
        titleLabel.setFont(new Font("Poppins", Font.PLAIN, 30));
        titleLabel.setForeground(new Color(109, 76, 65));
        titleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        container.add(titleLabel);

        diaryTextArea = new JTextArea(10, 40);
        diaryTextArea.setFont(new Font("Poppins", Font.PLAIN, 16));
        diaryTextArea.setLineWrap(true);
        diaryTextArea.setWrapStyleWord(true);
        diaryTextArea.setBorder(BorderFactory.createLineBorder(new Color(161, 136, 127), 1));
        diaryTextArea.setMargin(new Insets(10, 10, 10, 10));
        container.add(new JScrollPane(diaryTextArea));

        JPanel buttonsPanel = new JPanel();
        buttonsPanel.setLayout(new FlowLayout(FlowLayout.CENTER));

        JButton saveButton = new JButton("Save Entry");
        saveButton.setBackground(new Color(161, 136, 127));
        saveButton.setForeground(Color.WHITE);
        saveButton.setFont(new Font("Poppins", Font.PLAIN, 16));
        saveButton.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));
        saveButton.addActionListener(e -> saveEntry());
        buttonsPanel.add(saveButton);

        JButton viewButton = new JButton("View Previous Entries");
        viewButton.setBackground(new Color(161, 136, 127));
        viewButton.setForeground(Color.WHITE);
        viewButton.setFont(new Font("Poppins", Font.PLAIN, 16));
        viewButton.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));
        viewButton.addActionListener(e -> viewPreviousEntries());
        buttonsPanel.add(viewButton);

        container.add(buttonsPanel);

        JPanel calculatorPanel = new JPanel();
        calculatorPanel.setLayout(new BoxLayout(calculatorPanel, BoxLayout.Y_AXIS));
        calculatorPanel.setBackground(new Color(245, 245, 220));

        JLabel calcLabel = new JLabel("Quick Calculator");
        calcLabel.setFont(new Font("Poppins", Font.PLAIN, 20));
        calculatorPanel.add(calcLabel);

        calcInput = new JTextField(20);
        calculatorPanel.add(calcInput);

        JButton calcButton = new JButton("Calculate");
        calcButton.addActionListener(e -> calculate());
        calculatorPanel.add(calcButton);

        calcResult = new JLabel("Result: ");
        calculatorPanel.add(calcResult);


        JButton viewPreviousCalcButton = new JButton("View Previous Calculations");
        viewPreviousCalcButton.addActionListener(e -> viewPreviousCalculations());
        calculatorPanel.add(viewPreviousCalcButton);  
        container.add(calculatorPanel);

        JPanel reminderPanel = new JPanel();
        reminderPanel.setLayout(new BoxLayout(reminderPanel, BoxLayout.Y_AXIS));
        reminderPanel.setBackground(new Color(245, 245, 220));

        JLabel reminderLabel = new JLabel("Set a Reminder");
        reminderLabel.setFont(new Font("Poppins", Font.PLAIN, 20));
        reminderPanel.add(reminderLabel);

        reminderPanel.add(new JLabel("Select Date:"));
        reminderDate = new JTextField(10);
        reminderPanel.add(reminderDate);

        reminderPanel.add(new JLabel("Select Time:"));
        reminderTime = new JTextField(5);
        reminderPanel.add(reminderTime);

        JButton setReminderButton = new JButton("Set Notification");
        setReminderButton.addActionListener(e -> setReminder());
        reminderPanel.add(setReminderButton);

        reminderMessage = new JLabel();
        reminderPanel.add(reminderMessage);

        container.add(reminderPanel);

        frame.add(container, BorderLayout.CENTER);
        frame.setVisible(true);
    }

    private void saveEntry() {
        String diaryText = diaryTextArea.getText().trim();
        if (diaryText.isEmpty()) return;

        String date = new Date().toString();
        try (BufferedWriter writer = new BufferedWriter(new FileWriter("diaryEntries.txt", true))) {
            writer.write("Date: " + date + "\n" + "Entry: " + diaryText + "\n\n");
        } catch (IOException e) {
            e.printStackTrace();
        }
        diaryTextArea.setText("");
    }

    private void viewPreviousEntries() {
        try {
            String entries = new String(Files.readAllBytes(Paths.get("diaryEntries.txt")));
            JOptionPane.showMessageDialog(frame, entries, "Previous Entries", JOptionPane.INFORMATION_MESSAGE);
        } catch (IOException e) {
            JOptionPane.showMessageDialog(frame, "No entries found.", "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void calculate() {
        String input = calcInput.getText();
        try {
            if (input.isEmpty()) {
                calcResult.setText("Please enter an expression.");
                return;
            }

            double result = evaluateArithmeticExpression(input);
            calcResult.setText("Result: " + result);

            
            try (BufferedWriter writer = new BufferedWriter(new FileWriter("calculations.txt", true))) {
                writer.write(input + " = " + result + "\n");
            } catch (IOException e) {
                e.printStackTrace();
            }

        } catch (Exception e) {
            calcResult.setText("Invalid equation!");
        }
    }

    private double evaluateArithmeticExpression(String expression) throws Exception {
        expression = expression.replaceAll("\\s+", "");
        if (expression.isEmpty()) {
            throw new Exception("Empty expression.");
        }

        try {
            String[] operands = expression.split("[-+*/]");
            char operator = expression.charAt(operands[0].length());
            double operand1 = Double.parseDouble(operands[0]);
            double operand2 = Double.parseDouble(operands[1]);

            switch (operator) {
                case '+': return operand1 + operand2;
                case '-': return operand1 - operand2;
                case '*': return operand1 * operand2;
                case '/': 
                    if (operand2 == 0) throw new ArithmeticException("Cannot divide by zero");
                    return operand1 / operand2;
                default: throw new Exception("Unsupported operator");
            }
        } catch (Exception e) {
            throw new Exception("Invalid expression format.");
        }
    }

    private void viewPreviousCalculations() {
        try {
            String calculations = new String(Files.readAllBytes(Paths.get("calculations.txt")));
            JOptionPane.showMessageDialog(frame, calculations, "Previous Calculations", JOptionPane.INFORMATION_MESSAGE);
        } catch (IOException e) {
            JOptionPane.showMessageDialog(frame, "No calculations found.", "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void setReminder() {
        String date = reminderDate.getText();
        String time = reminderTime.getText();
        if (date.isEmpty() || time.isEmpty()) {
            reminderMessage.setText("Please select both date and time!");
            return;
        }
        reminderMessage.setText("Reminder set for " + date + " at " + time + "!");
    }
}
