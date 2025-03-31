import React, { useState } from "react";
import { Link } from "react-router-dom";
import { leadService } from "../services/api";

function LeadForm() {
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    resume: null,
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState("");

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });

    // Clear field error when user starts typing again
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: "",
      });
    }

    // Clear submission messages when user changes input
    if (submitSuccess) setSubmitSuccess(false);
    if (submitError) setSubmitError("");
  };

  // Handle file input changes
  const handleFileChange = (e) => {
    const file = e.target.files[0];

    if (file) {
      // Validate file type (PDF, DOC, DOCX)
      const validTypes = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      ];

      if (!validTypes.includes(file.type)) {
        setErrors({
          ...errors,
          resume: "Please upload a PDF, DOC, or DOCX file",
        });
        e.target.value = "";
        return;
      }

      // Validate file size (5MB max)
      const maxSize = 5 * 1024 * 1024; // 5MB in bytes

      if (file.size > maxSize) {
        setErrors({
          ...errors,
          resume: "File size must be less than 5MB",
        });
        e.target.value = "";
        return;
      }

      // Clear resume error if exists
      if (errors.resume) {
        setErrors({
          ...errors,
          resume: "",
        });
      }

      setFormData({
        ...formData,
        resume: file,
      });
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};

    if (!formData.first_name.trim()) {
      newErrors.first_name = "First name is required";
    }

    if (!formData.last_name.trim()) {
      newErrors.last_name = "Last name is required";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email is invalid";
    }

    if (!formData.resume) {
      newErrors.resume = "Resume is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (validateForm()) {
      setIsSubmitting(true);
      setSubmitSuccess(false);
      setSubmitError("");

      try {
        await leadService.submitLead(formData);

        // Reset form on success
        setFormData({
          first_name: "",
          last_name: "",
          email: "",
          resume: null,
        });

        // Reset file input
        const fileInput = document.getElementById("resume");
        if (fileInput) fileInput.value = "";

        setSubmitSuccess(true);
      } catch (error) {
        setSubmitError(error.toString());
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  return (
    <div className="container my-5">
      <div className="row">
        <div className="col-lg-8 offset-lg-2">
          <div className="card shadow">
            <div className="card-body p-4">
              <h2 className="card-title text-center mb-4">Submit Your Lead</h2>

              {submitSuccess && (
                <div className="alert alert-success" role="alert">
                  <h5 className="alert-heading">
                    Thank you for your submission!
                  </h5>
                  <p>
                    We've received your information and will contact you soon.
                  </p>
                </div>
              )}

              {submitError && (
                <div className="alert alert-danger" role="alert">
                  <h5 className="alert-heading">Submission Error</h5>
                  <p>{submitError}</p>
                </div>
              )}

              <form onSubmit={handleSubmit} encType="multipart/form-data">
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label htmlFor="first_name" className="form-label">
                      First Name
                    </label>
                    <input
                      type="text"
                      className={`form-control ${errors.first_name ? "is-invalid" : ""}`}
                      id="first_name"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleChange}
                      placeholder="Enter your first name"
                    />
                    {errors.first_name && (
                      <div className="invalid-feedback">
                        {errors.first_name}
                      </div>
                    )}
                  </div>

                  <div className="col-md-6 mb-3">
                    <label htmlFor="last_name" className="form-label">
                      Last Name
                    </label>
                    <input
                      type="text"
                      className={`form-control ${errors.last_name ? "is-invalid" : ""}`}
                      id="last_name"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleChange}
                      placeholder="Enter your last name"
                    />
                    {errors.last_name && (
                      <div className="invalid-feedback">{errors.last_name}</div>
                    )}
                  </div>
                </div>

                <div className="mb-3">
                  <label htmlFor="email" className="form-label">
                    Email
                  </label>
                  <input
                    type="email"
                    className={`form-control ${errors.email ? "is-invalid" : ""}`}
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="Enter your email"
                  />
                  {errors.email && (
                    <div className="invalid-feedback">{errors.email}</div>
                  )}
                </div>
                <div className="mb-3">
                  <label htmlFor="resume" className="form-label">
                    Resume <span className="text-danger">*</span>
                  </label>
                  <input
                    type="file"
                    className={`form-control ${errors.resume ? "is-invalid" : ""}`}
                    id="resume"
                    name="resume"
                    onChange={handleFileChange}
                    accept=".pdf,.doc,.docx"
                    required
                  />
                  <div className="form-text">
                    Upload your resume (PDF, DOC, or DOCX, max 5MB)
                  </div>
                  {errors.resume && (
                    <div className="invalid-feedback">{errors.resume}</div>
                  )}
                </div>

                <div className="d-grid gap-2 mt-4">
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <>
                        <span
                          className="spinner-border spinner-border-sm me-2"
                          role="status"
                          aria-hidden="true"
                        ></span>
                        Submitting...
                      </>
                    ) : (
                      "Submit Information"
                    )}
                  </button>
                </div>
              </form>

              <div className="mt-4 text-center">
                <Link to="/login" className="text-decoration-none">
                  Attorney Login
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LeadForm;
