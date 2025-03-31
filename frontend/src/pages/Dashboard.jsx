import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { leadService } from "../services/api";
import NavBar from "../components/NavBar";

function Dashboard() {
  // Local state declarations
  const [leads, setLeads] = useState([]);
  const [filteredLeads, setFilteredLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterState, setFilterState] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [totalLeads, setTotalLeads] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  // Track the lead currently being updated (for disabling the update button)
  const [updatingLeadId, setUpdatingLeadId] = useState(null);

  const { isAuthenticated, isAttorney } = useAuth();
  const navigate = useNavigate();

  // Redirect unauthorized users immediately
  useEffect(() => {
    if (!isAuthenticated() || !isAttorney()) {
      navigate("/login");
    }
  }, [isAuthenticated, isAttorney, navigate]);

  // Function to fetch leads from the API, wrapped in useCallback to avoid unnecessary re-creation.
  const fetchLeads = useCallback(async () => {
    try {
      setLoading(true);
      const data = await leadService.getAllLeads(
        filterState || null,
        page,
        pageSize,
        searchQuery.trim() || null,
      );
      // Update state with the returned data
      setLeads(data.leads);
      setFilteredLeads(data.leads);
      setTotalLeads(data.total);
      setError(null);
    } catch (err) {
      console.error("Error fetching leads:", err);
      setError("Failed to load leads. Please try again later.");
    } finally {
      setLoading(false);
    }
  }, [filterState, page, pageSize, searchQuery]);

  // Fetch leads whenever the filtering, pagination, or search criteria change.
  useEffect(() => {
    if (isAuthenticated() && isAttorney()) {
      fetchLeads();
    }
  }, [fetchLeads, isAuthenticated, isAttorney]);

  // Event handlers for filtering, searching, and pagination
  const handleFilterChange = (e) => {
    setFilterState(e.target.value);
    setPage(1); // Reset to the first page when filter changes
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value.toLowerCase());
    setPage(1); // Reset to the first page when search query changes
  };

  const handlePageSizeChange = (e) => {
    setPageSize(Number(e.target.value));
    setPage(1); // Reset to the first page when page size changes
  };

  // Toggle lead status and refresh the list once updated
  const updateLeadStatus = async (lead) => {
    const newState = lead.state === "PENDING" ? "REACHED_OUT" : "PENDING";
    const updateData = { state: newState };

    try {
      setUpdatingLeadId(lead.id);
      await leadService.updateLead(lead.id, updateData);
      await fetchLeads();
    } catch (err) {
      console.error("Error updating lead status:", err);
      alert("Failed to update lead status. Please try again.");
    } finally {
      setUpdatingLeadId(null);
    }
  };

  const totalPages = Math.ceil(totalLeads / pageSize);

  // Generate pagination buttons dynamically
  const paginationButtons = [];
  for (let i = 1; i <= totalPages; i++) {
    paginationButtons.push(
      <li key={i} className={`page-item ${page === i ? "active" : ""}`}>
        <button className="page-link" onClick={() => setPage(i)}>
          {i}
        </button>
      </li>,
    );
  }

  return (
    <>
      <NavBar />
      <div className="container mt-4">
        <div className="card shadow">
          <div className="card-header bg-primary text-white">
            <h3 className="mb-0">Lead Management Dashboard</h3>
          </div>
          <div className="card-body">
            {/* Filter, Search, and Page Size Controls */}
            <div className="row mb-4">
              <div className="col-md-4">
                <div className="input-group">
                  <span className="input-group-text">Filter by State</span>
                  <select
                    className="form-select"
                    value={filterState}
                    onChange={handleFilterChange}
                  >
                    <option value="">All Leads</option>
                    <option value="PENDING">Pending</option>
                    <option value="REACHED_OUT">Reached Out</option>
                  </select>
                </div>
              </div>

              <div className="col-md-4">
                <div className="input-group">
                  <span className="input-group-text">Search</span>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Search by name or email"
                    value={searchQuery}
                    onChange={handleSearchChange}
                  />
                </div>
              </div>

              <div className="col-md-4">
                <div className="input-group">
                  <span className="input-group-text">Page Size</span>
                  <select
                    className="form-select"
                    value={pageSize}
                    onChange={handlePageSizeChange}
                  >
                    <option value="5">5 per page</option>
                    <option value="10">10 per page</option>
                    <option value="25">25 per page</option>
                    <option value="50">50 per page</option>
                    <option value="100">100 per page</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Conditional Rendering: Loading, Error, or Data Table */}
            {loading ? (
              <div className="text-center my-5">
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
                <p className="mt-2">Loading leads...</p>
              </div>
            ) : error ? (
              <div className="alert alert-danger" role="alert">
                {error}
              </div>
            ) : (
              <>
                <div className="table-responsive">
                  <table className="table table-striped table-hover">
                    <thead className="table-light">
                      <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Status</th>
                        <th>Submitted</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredLeads.length === 0 ? (
                        <tr>
                          <td colSpan="6" className="text-center py-4">
                            No leads found.{" "}
                            {searchQuery && "Try a different search term."}
                          </td>
                        </tr>
                      ) : (
                        filteredLeads.map((lead) => (
                          <tr key={lead.id}>
                            <td>
                              {lead.first_name} {lead.last_name}
                            </td>
                            <td>{lead.email}</td>
                            <td>
                              <span
                                className={`badge ${
                                  lead.state === "PENDING"
                                    ? "bg-warning"
                                    : "bg-success"
                                }`}
                              >
                                {lead.state.replace("_", " ")}
                              </span>
                            </td>
                            <td>
                              {new Date(lead.created_at).toLocaleDateString()}
                            </td>
                            <td>
                              <div className="btn-group">
                                <button
                                  className={`btn btn-sm ${
                                    lead.state === "PENDING"
                                      ? "btn-success"
                                      : "btn-warning"
                                  }`}
                                  onClick={() => updateLeadStatus(lead)}
                                  disabled={updatingLeadId === lead.id}
                                >
                                  {updatingLeadId === lead.id ? (
                                    <>
                                      <span
                                        className="spinner-border spinner-border-sm me-2"
                                        role="status"
                                        aria-hidden="true"
                                      ></span>
                                      Updating...
                                    </>
                                  ) : lead.state === "PENDING" ? (
                                    "Mark as Reached Out"
                                  ) : (
                                    "Mark as Pending"
                                  )}
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>

                {/* Pagination Controls */}
                {totalPages > 1 && (
                  <nav aria-label="Lead pagination" className="mt-4">
                    <ul className="pagination justify-content-center">
                      <li
                        className={`page-item ${page === 1 ? "disabled" : ""}`}
                      >
                        <button
                          className="page-link"
                          onClick={() => setPage(page - 1)}
                          disabled={page === 1}
                        >
                          Previous
                        </button>
                      </li>
                      {paginationButtons}
                      <li
                        className={`page-item ${
                          page === totalPages ? "disabled" : ""
                        }`}
                      >
                        <button
                          className="page-link"
                          onClick={() => setPage(page + 1)}
                          disabled={page === totalPages}
                        >
                          Next
                        </button>
                      </li>
                    </ul>
                  </nav>
                )}

                <div className="text-center mt-3">
                  <p className="text-muted">
                    Showing {filteredLeads.length} of {totalLeads} total leads
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default Dashboard;
